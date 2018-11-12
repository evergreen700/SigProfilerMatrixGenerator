#!/usr/bin/env python3

import sigProfilerMatrixGenerator as matGen
import os
import re
import sys
import logging
import pandas as pd
import datetime
import convert_input_to_simple_files as convertIn
import uuid

def sigProfilerMatrixGeneratorFunc (project, genome, exome=False, SNVs=False,indel=False, indel_extended=False, bed_file=None, chrom_based=False, plot=False, gs=False):
	'''
	Allows for the import of the sigProfilerMatrixGenerator.py function. Returns a dictionary
	with each context serving as the first level of keys. 

	Parameters:
			   project  -> unique name given to the current samples
				genome  -> reference genome 
				 exome  -> flag to use only the exome or not
				 indel  -> flag to create the matrix for the limited indel matrix
		indel_extended  -> flag to create the regular, extended INDEL matrix
			  bed_file  -> BED file that contains a list of ranges to be used in generating the matrices

	Returns:
			  matrices  -> dictionary (nested) of the matrices for each context

		example:
			matrices = {'96': {'PD1001a':{'A[A>C]A':23,
										 'A[A>G]A':10,...},
							  'PD1202a':{'A[A>C]A':23,
										 'A[A>G]A':10,...},...},
						'192':{'PD1001a':{'T:A[A>C]A':23,
										 'T:A[A>G]A':10,...},
							  'PD1202a':{'T:A[A>C]A':23,
										 'T:A[A>G]A':10,...},...},...}
	'''

	# Instantiates all of the required variables
	functionFlag = True
	bed = False
	bed_ranges = None
	indel = indel
	if indel:
		limited_indel = True
	exome = exome
	plot = plot
	if plot:
		indel = True

	matrices = {'96':None, '1536':None, '192':None, '3072':None, 'DINUC':None, '6':None, '12':None}

	# Adjusts the variables if the context is for INDELs
	if indel:
		matrices = {'INDEL':None}

	ncbi_chrom = {'NC_000067.6':'1', 'NC_000068.7':'2', 'NC_000069.6':'3', 'NC_000070.6':'4', 
				  'NC_000071.6':'5', 'NC_000072.6':'6', 'NC_000073.6':'7', 'NC_000074.6':'8',
				  'NC_000075.6':'9', 'NC_000076.6':'10', 'NC_000077.6':'11', 'NC_000078.6':'12',
				  'NC_000079.6':'13', 'NC_000080.6':'14', 'NC_000081.6':'15', 'NC_000082.6':'16', 
				  'NC_000083.6':'17', 'NC_000084.6':'18', 'NC_000085.6':'19', 'NC_000086.7':'X', 
				  'NC_000087.7':'Y'}
				  
	tsb_ref = {0:['N','A'], 1:['N','C'], 2:['N','G'], 3:['N','T'],
			   4:['T','A'], 5:['T','C'], 6:['T','G'], 7:['T','T'],
			   8:['U','A'], 9:['U','C'], 10:['U','G'], 11:['U','T'],
			   12:['B','A'], 13:['B','C'], 14:['B','G'], 15:['B','T'],
			   16:['N','N'], 17:['T','N'], 18:['U','N'], 19:['B','N']}


	contexts = ['3072', 'DINUC']


	# Organizes all of the reference directories for later reference:
	current_dir = os.getcwd()
	ref_dir = re.sub('\/scripts$', '', current_dir)
	chrom_path =ref_dir + '/references/chromosomes/tsb/' + genome + "/"
	transcript_path = ref_dir + '/references/chromosomes/transcripts/' + genome + "/"

	time_stamp = datetime.date.today()
	output_log_path = ref_dir + "/logs/"
	if not os.path.exists(output_log_path):
		os.system("mkdir " + output_log_path)
	error_file = output_log_path + 'SigProfilerMatrixGenerator_' + project + "_" + genome + str(time_stamp) + ".err"
	log_file = output_log_path + 'SigProfilerMatrixGenerator_' + project + "_" + genome + str(time_stamp) + ".out"
	if os.path.exists(error_file):
		os.system("rm " + error_file)
	if os.path.exists(log_file):
		 os.system("rm " + log_file)
	sys.stderr = open(error_file, 'w')
	logging.basicConfig(filename=log_file, level=logging.INFO)

	# Organizes all of the input and output directories:
	output_matrix = ref_dir + "/references/matrix/"
	vcf_path = ref_dir + '/references/vcf_files/' + project + "/"

	# Gathers all of the vcf files:
	if SNVs:
		vcf_files_snv_temp = os.listdir(vcf_path + "SNV/")
	if indel:
		vcf_files_indel_temp = os.listdir(vcf_path + "INDEL/")

	vcf_files2 = [[],[]]

	if SNVs:
		for file in vcf_files_snv_temp:
			# Skips hidden files
			if file[0:3] == '.DS':
				pass
			else:
				vcf_files2[0].append(file)

	if indel:
		for file in vcf_files_indel_temp:
			# Skips hidden files
			if file[0:3] == '.DS':
				pass
			else:
				vcf_files2[1].append(file)


	for i in range(0, len(vcf_files2), 1):
		if i ==1 and indel:
			contexts = ['INDEL']
		elif i == 1 and not indel:
			break
		elif i == 0 and not SNVs:
			continue
		vcf_path = ref_dir + '/references/vcf_files/' + project + "/"
		file_name = vcf_files2[i][0].split(".")
		file_extension = file_name[-1]

		unique_folder = project + str(uuid.uuid4())
		#output_path = ref_dir + "/references/vcf_files/single/"
		output_path = ref_dir + "/references/vcf_files/" + unique_folder + "/"
		if not os.path.exists(output_path):
			os.makedirs(output_path)

		if file_extension == 'genome':
			if i ==1:
				convertIn.convertTxt(project, vcf_path + "INDEL/", genome, output_path, 'INDEL')
				#os.system("bash convert_txt_files_to_simple_files.sh " + project + " " + vcf_path + "INDEL/")
			else:
				convertIn.convertTxt(project, vcf_path + "SNV/", genome, output_path, 'SNV')
				#os.system("bash convert_txt_files_to_simple_files.sh " + project + " " + vcf_path + "SNV/")
		else:
			if i == 1:
				if file_extension == 'txt':
					convertIn.convertTxt(project, vcf_path + "INDEL/",  genome,  output_path,'INDEL')
				elif file_extension == 'vcf':
					convertIn.convertVCF(project, vcf_path + "INDEL/",  genome, output_path,'INDEL')
				elif file_extension == 'maf':
					convertIn.convertMAF(project, vcf_path + "INDEL/",  genome, output_path, 'INDEL')
				elif file_extension == '.tsv':
					convertIn.convertICGC(project, vcf_path + "INDEL/",  genome, output_path,'INDEL')
				else:
					print("File format not supported")

				#os.system("bash convert_" + file_extension + "_files_to_simple_files.sh " + project + " " + vcf_path + "INDEL/")
			else:
				if file_extension == 'txt':
					convertIn.convertTxt(project, vcf_path + "SNV/",  genome, output_path,'SNV')
				elif file_extension == 'vcf':
					convertIn.convertVCF(project, vcf_path + "SNV/",  genome, output_path,'SNV')
				elif file_extension == 'maf':
					convertIn.convertMAF(project, vcf_path + "SNV/",  genome, output_path, 'SNV')
				elif file_extension == '.tsv':
					convertIn.convertICGC(project, vcf_path + "SNV/",  genome, output_path, 'SNV')
				else:
					print("File format not supported")

				#os.system("bash convert_" + file_extension + "_files_to_simple_files.sh " + project + " " + vcf_path +"SNV/")

		vcf_files = os.listdir(output_path)
		vcf_path = output_path

		sort_file = vcf_files[0]
		with open(vcf_path + sort_file) as f:
			lines = [line.strip().split() for line in f]

		output = open(vcf_path + sort_file, 'w')

		for line in sorted(lines, key = lambda x: (['X','Y','1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20', '21', '22'].index(x[5]), x[1], x[6])):
			print('\t'.join(line), file=output)

		output.close()

		print("Sorting complete...\nDetermining mutation type for each variant, one chromosome at a time. Starting catalogue generation...")

		if bed_file != None:
			bed = True
			bed_file_path = ref_dir + "/references/vcf_files/BED/" + project + "/" + bed_file
			bed_ranges = matGen.BED_filtering(bed_file_path)

		# Creates the matrix for each context
		for context in contexts:
			if context != 'DINUC' and context != 'INDEL':
				matrix = matGen.catalogue_generator_single (vcf_path, vcf_files, chrom_path, project, output_matrix, context, exome, genome, ncbi_chrom, functionFlag, bed, bed_ranges, chrom_based, plot, tsb_ref, transcript_path, gs)
				matrices = matrix

			elif context == 'DINUC':
				matrix = matGen.catalogue_generator_DINUC_single (vcf_path, vcf_files, chrom_path, project, output_matrix, exome, genome, ncbi_chrom, functionFlag, bed, bed_ranges, chrom_based, plot, tsb_ref)
				matrices[context] = matrix

			elif context == 'INDEL':
				matrix = matGen.catalogue_generator_INDEL_single (vcf_path, vcf_files, chrom_path, project, output_matrix, exome, genome, ncbi_chrom, limited_indel, functionFlag, bed, bed_ranges, chrom_based, plot, tsb_ref, transcript_path, gs)
				matrices[context] = matrix

			# Deletes the temporary files and returns the final matrix
			logging.info("Catalogue for " + context + " context is complete.")
			print("Catalogue for " + context + " context is complete.")
		os.system("rm -r " + vcf_path)

	final_matrices = {}
	for conts in matrices.keys():
		final_matrices[conts] = pd.DataFrame.from_dict(matrices[conts])
		for column in final_matrices[conts].columns:
			final_matrices[conts][column] = matrices[conts][column].fillna(0)
	return(final_matrices)

	