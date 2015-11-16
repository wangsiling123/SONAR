
from .. import *
import threading
from Bio.Blast.Applications import NcbiblastnCommandline



class blastThread (threading.Thread):
	def __init__(self, threadID, fasta, db, output, wordSize):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.fasta    = fasta
		self.db       = db
		self.output   = output
		self.wordSize = wordSize
	def run(self):
		cline = NcbiblastnCommandline(blast_cmd, query=self.fasta, db=self.db, out=self.output,
					      outfmt="\'6 qseqid sseqid pident length mismatch gaps qstart qend sstart send evalue bitscore sstrand\'",
					      gapopen=5, gapextend=2, penalty=-1, reward=1, evalue=1e-3, max_target_seqs=10, word_size=self.wordSize)
		cline()



def get_top_hits(infile, topHitWriter=None, dict_germ_count=dict(), maxQEnd=dict(), minQStart=dict()):
	"""retrieve top hits from all result files"""
	
	dict_germ_aln    =  dict()
	dict_other_germs =  dict()
	old_id           =  ""


	reader = csv.reader(open(infile, "rU"), delimiter = sep)
	for row in reader:

		if len(row) != 13:
			pass;

		else:
                        my_alignment = MyAlignment(row)

                        if my_alignment.qid != old_id:
                                if old_id != "":
					aline = best_row
                                        if len(others)>0:
                                                aline.append(",".join(others))
                                                dict_other_germs[best_alignment.qid] = others

                                        if topHitWriter is not None:
                                                topHitWriter.writerow(aline)
                                                if len(second_match)>0:
                                                        topHitWriter.writerow(second_match)

                                        dict_germ_aln[best_alignment.qid] = best_alignment

                                        if best_alignment.sid not in dict_germ_count:
                                                dict_germ_count[best_alignment.sid] 	= 0
                                        dict_germ_count[best_alignment.sid] 		+= 1

						
                                #skips D genes that matched 5' J
                                if my_alignment.qend > maxQEnd.get(my_alignment.qid, 999):
                                        old_id=""
                                        continue

                                #skips C genes that matched 3' J (not sure if necessary)
                                if my_alignment.qstart < minQStart.get(my_alignment.qid, -1):
                                        old_id=""
                                        continue

				old_id = my_alignment.qid
				best_alignment = my_alignment
				best_row = row
				others = []
				second_match = []
				
			else:
				#added 20150107 by CAS
				'''
				need three conditions:
				1. hit is on same gene
				2. hit is on same strand
				3. hits are non-overlapping
				'''
				if my_alignment.sid == best_alignment.sid and my_alignment.strand == best_alignment.strand and (max(my_alignment.sstart, my_alignment.send)<min(best_alignment.sstart,best_alignment.send) or min(my_alignment.sstart, my_alignment.send)>max(best_alignment.sstart,best_alignment.send)):
					second_match = row
					#change boundaries of alignment on both query and hit (to get J properly)
					if my_alignment.send < best_alignment.sstart:
						best_alignment.sstart = my_alignment.sstart
						if best_alignment.strand == "plus":
							best_alignment.qstart = my_alignment.qstart
						else:
							best_alignment.qend = my_alignment.qend
					else:
						best_alignment.send = my_alignment.send
						if best_alignment.strand == "plus":
							best_alignment.qend = my_alignment.qend
						else:
							best_alignment.qstart = my_alignment.qstart

						
				elif my_alignment.score <= best_alignment.score - 3:
					others.append(my_alignment.sid)

        #last line, repeat of what's in the loop
        if old_id != "":
                aline = best_row
                if len(others)>0:
                        aline.append(",".join(others))
                        dict_other_germs[best_alignment.qid] = others

                if topHitWriter is not None:
                        topHitWriter.writerow(aline)
                        if len(second_match)>0:
                                topHitWriter.writerow(second_match)

                dict_germ_aln[best_alignment.qid] = best_alignment

                if best_alignment.sid not in dict_germ_count:
                        dict_germ_count[best_alignment.sid] 	= 0
                dict_germ_count[best_alignment.sid] 		+= 1


        #warns user if blast crashed for some reason
	if len(dict_germ_aln) == 0:
		print("%s appears to be empty..."%infile)


	return dict_germ_aln, dict_other_germs, dict_germ_count
