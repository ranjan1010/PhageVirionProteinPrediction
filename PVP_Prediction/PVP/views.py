import os
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from .forms import File_Form
from .models import File_Profile
import pandas as pd
from .models import Execute_Load_Predict

# Create your views here.
def home(request):
    return render(request,'home.html')

def submission(request):
    form = File_Form()
    if request.method == 'POST':
        form = File_Form(request.POST, request.FILES)
        # print("Before Valid ,,,,")
        if form.is_valid():
            file_pr = form.save(commit=False)
            inputData = file_pr.textFile
            # print("Before if >>>")
            if inputData != "":
                print(inputData)
                inputData = inputData.rstrip()
                # print(">>>>>", inputData)
                f = open(os.path.join(settings.MEDIA_ROOT, "inputSequence.fasta"),"w+")
                f.write(inputData)
                print(f.read())
                f.close()
            #file_pr.fasta_file = request.FILES['fasta_file']
            else:
                file_pr.fasta_file.name = 'inputSequence.fasta'
                if os.path.exists(os.path.join(settings.MEDIA_ROOT, file_pr.fasta_file.name)):
                    os.remove(os.path.join(settings.MEDIA_ROOT, file_pr.fasta_file.name))
                # print("Before file save.....")
                file_pr.save()
                # print("After file save.....")
            return prediction(request, os.path.join(settings.MEDIA_ROOT, 'inputSequence.fasta'))
            #return render(request, 'predictionResult.html', {'file_pr': file_pr})
    context = {"form": form, }
    return render(request, 'submission.html', context)

def help(request):
    return render(request, 'help.html')

def team(request):
    return render(request, 'team.html')

def contact(request):
    return render(request, 'contact.html')

def prediction(request, inputFile):
    objOfELP = Execute_Load_Predict()
    objOfELP.main_program("ModelForGBC", inputFile)
    result_table = pd.read_csv("Predition_Result_inputSequence.csv")
    result_table_all = result_table[result_table.columns[0:3]].values
    return render(request, 'predictionResult.html', {'result_all': result_table_all})
