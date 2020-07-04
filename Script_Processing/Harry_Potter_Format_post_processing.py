import re
import os

files = [f for f in os.listdir() if f[-4:] == ".txt" and f[-10:-4] != "SCRIPT"]

EMPTY_STRING=re.compile('\s+',re.U)
SCRIPT_SPEAKER =re.compile('_',re.U)
skip_line = re.compile('\n',re.U)
omitted = re.compile('.*OMITTED',re.U)
end_number = re.compile('\s+[A-Z]?[1-9]+\.?\s+',re.U)
begin_number = re.compile('[1-9]+',re.U)
scene_number = re.compile('[A-Z]+[1-9]+(  +)',re.U)
space_context = re.compile('^ {1,9}',re.U)
parenthesis_dialog = re.compile('^  +(\(\w)',re.U)
blue_draft = re.compile('^ +BLUE DRAFT', re.U)
speaker = re.compile('^ +([A-Z])', re.U)
multiple_space = re.compile('  +', re.U)
scene = re.compile('^Scene:', re.U)
dialog = re.compile('^(.*): (.*)', re.U)

for f in files:
    print(f, f[-9:-4])
    file1 = open(f, "r")
    Lines = file1.readlines() 
    New_lines = []
    for index in range(len(Lines)):
        if not skip_line.match(Lines[index]) :
            if scene.match(Lines[index]):
                Lines[index] = "\n"
            Lines[index] = dialog.sub(r'_\g<1>\n"\g<2>"', Lines[index])
            
            Lines[index] = multiple_space.sub(r' ', Lines[index])

            New_lines.append(Lines[index])
            
            

    Lines = New_lines
    New_lines = []
    lastline = ""
    current_string = ""
    dialog = re.compile('^"',re.U)
    speaker = re.compile('^_',re.U)
    for index in range(len(Lines)):
        if speaker.match(Lines[index]) or EMPTY_STRING.match(Lines[index]):
            if lastline != "":
                New_lines.append(current_string)
            New_lines.append(Lines[index])
            lastline = ""
        elif dialog.match(Lines[index]):
            if lastline == "dialog":
                current_string = current_string[:-2] + " " + Lines[index][1:]
            else: 
                if lastline == "context":
                    New_lines.append(current_string)
                current_string = Lines[index]
                lastline = "dialog"
        else:
            if lastline == "context":
                current_string = current_string[:-2] + " " + Lines[index][1:]
            else: 
                if lastline == "dialog":
                    New_lines.append(current_string)
                current_string = Lines[index]
                lastline = "context"
                    
        
        
    file1.close()


    file2 = open(f[:-4]+"_SCRIPT.txt", "w")
    file2.writelines(New_lines)
    file2.close()