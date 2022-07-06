from django.db import models
from django.core.validators import FileExtensionValidator
import os
import pandas as pd
import pickle
from protlearn.features import aac
from protlearn.features import ngram
from sklearn.ensemble import GradientBoostingClassifier

# Create your models here.
class File_Profile(models.Model):
    textFile = models.CharField(max_length=200000, blank=True)
    fasta_file = models.FileField(blank=True, null=True,validators=[FileExtensionValidator(allowed_extensions=["fasta"])])
    job = models.CharField(max_length=200, blank=True)
    email = models.EmailField(default=None, blank=True)

class Execute_Load_Predict():
    # this function will generate prediction(input) and outcome(output) variable for main dataset
    def data_generation_train():

        data_table = pd.read_csv("Training_Dataset_AAC_DPC.csv")

        last_index_column = len(data_table.columns)

        pred_data = data_table[data_table.columns[1: last_index_column]].values
        outcome_data = data_table[data_table.columns[0]].values

        print("Inside data generator........")

        return pred_data, outcome_data

    def read_fasta(self, input_fasta_file):
        fasta_header = []
        fasta_sequences = []
        temp_sequence = None

        file_fasta = open(input_fasta_file)
        file_lines = file_fasta.readlines()

        for line in file_lines:
            line = line.rstrip()
            #print("~~~~~~~~~~~~~~~~Line~~~~~~~~~", line)
            if line.startswith(">"):
                fasta_header.append(line.replace(">",""))
                # this section use to append all sequence expect last
                #print("===========Temp Sequence======", temp_sequence)
                if temp_sequence:
                    # these replace are use to few error AA to known ones
                    temp_seq_replace1 = temp_sequence.replace("U", "A")
                    temp_seq_replace2 = temp_seq_replace1.replace("X", "C")
                    temp_seq_replace3 = temp_seq_replace2.replace("B", "D")
                    temp_seq_replace4 = temp_seq_replace3.replace("J", "E")
                    temp_seq_replace5 = temp_seq_replace4.replace("Z", "F")
                    temp_seq_replace6 = temp_seq_replace5.replace("O", "G")
                    temp_seq_replace7 = temp_seq_replace6.replace(" ", "")
                    temp_seq_replace8 = temp_seq_replace7.replace("  ", "")
                    temp_seq_replace9 = temp_seq_replace8.replace("   ", "")
                    fasta_sequences.append(temp_seq_replace9)

                temp_sequence = ''
            else:
                temp_sequence += line
                #print("-------------------Else Temp Seq-------------", temp_sequence)
            # this section use to append last sequence
        #print("+++++++++++++++++outside  Temp Seq++++++++++++", temp_sequence)
        if temp_sequence:
            # these replace are use to few error AA to known ones
            temp_seq_replace1 = temp_sequence.replace("U", "A")
            temp_seq_replace2 = temp_seq_replace1.replace("X", "C")
            temp_seq_replace3 = temp_seq_replace2.replace("B", "D")
            temp_seq_replace4 = temp_seq_replace3.replace("J", "E")
            temp_seq_replace5 = temp_seq_replace4.replace("Z", "F")
            temp_seq_replace6 = temp_seq_replace5.replace("O", "G")
            temp_seq_replace7 = temp_seq_replace6.replace(" ", "")
            temp_seq_replace8 = temp_seq_replace7.replace("  ", "")
            temp_seq_replace9 = temp_seq_replace8.replace("   ", "")
            fasta_sequences.append(temp_seq_replace9)
        #print("Fasta header:", fasta_header,"Sequence:", fasta_sequences)
        return fasta_header, fasta_sequences

    def sequence_features_generator(self, protein_sequences):

        Protein_AAComp, Protein_AAC_header = aac(protein_sequences, remove_zero_cols=False)
        Protein_DPcomp, Protein_DPcomp_header = ngram(protein_sequences, n=2)

        return Protein_AAComp, Protein_AAC_header, Protein_DPcomp, Protein_DPcomp_header

    # this function will generate prediction(input) and outcome(output) variable for main dataset
    def data_generation(input_file):

        data_table = pd.read_csv(input_file)

        last_index_column = len(data_table.columns)

        pred_data = data_table[data_table.columns[1: last_index_column]].values
        outcome_data = data_table[data_table.columns[0]].values

        print("Inside data generator........")

        return pred_data, outcome_data

    def main_program(self, model_file, input_file):

        pred_var_train, out_var_train = Execute_Load_Predict.data_generation_train()
        GBC = GradientBoostingClassifier(n_estimators=100, random_state=42)
        # for generate sequence composition features from fasta file
        print(":::::::input file ::::::::", input_file)
        protein_seq_header, protein_seq = Execute_Load_Predict().read_fasta(input_file)
        sequence_AAC_composition, sequence_AAC_composition_header, sequence_DPC_composition, \
        sequence_DPC_composition_header = Execute_Load_Predict().sequence_features_generator(protein_seq)

        max_seq = len(protein_seq)
        print("----------Total number of sequences:-------", max_seq)

        result_sequence_AAC_composition = pd.DataFrame(data=sequence_AAC_composition,
                                                       columns=list(sequence_AAC_composition_header))
        result_sequence_DPC_composition = pd.DataFrame(data=sequence_DPC_composition,columns=sequence_DPC_composition_header)

        # Concatenate all the different protein composition horizontally (used axis = 1)
        result_sequence_composition = pd.concat([result_sequence_AAC_composition, result_sequence_DPC_composition], axis=1)
        # this will add a sequence header column to dataframe
        result_sequence_composition.insert(loc=0, column="class_label", value=0)
        result_sequence_composition.to_csv("Seq_Comp_AAC_DPC_" + str(os.path.basename(input_file)).replace(".fasta", ".csv"), index=False)

        input_sequence_composition_fileName = "Seq_Comp_AAC_DPC_" + str(os.path.basename(input_file)).replace(".fasta", ".csv")
        pred_var, out_var = Execute_Load_Predict.data_generation(input_sequence_composition_fileName)

        model_GBC_save = GBC.fit(pred_var_train, out_var_train)

        # Then Save it with picke.dump
        pickle_out = open("./model.sav", "wb")
        pickle.dump(model_GBC_save, pickle_out)
        pickle_out.close()

        loaded_model = pickle.load(open('model.sav', 'rb'))

        result_predict = loaded_model.predict(pred_var)
        result_probability = loaded_model.predict_proba(pred_var)
        result_predict_class = []
        for res_prob in list(result_probability[:,1]):
            if res_prob > 0.5:
                result_predict_class.append('Virion Protein')
            else:
                result_predict_class.append('Non-Virion Protein')
        print(result_predict)
        print(result_predict_class)
        print(result_probability[:, 1])
        final_result_prediction = pd.DataFrame(list(zip(protein_seq_header, list(result_probability[:,1]), list(result_predict_class))), columns=['SequenceName', 'PredictionScore', 'PredictedClass'])
        final_result_prediction.to_csv("Predition_Result_" + str(os.path.basename(input_file)).replace(".fasta", ".csv"), index=False)
