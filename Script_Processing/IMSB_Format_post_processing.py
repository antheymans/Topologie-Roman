import re

EMPTY_STRING=re.compile('\s+',re.U)
SCRIPT_SPEAKER =re.compile('_',re.U)
skip_line = re.compile('\n',re.U)
omitted = re.compile('.*OMITTED',re.U)
#end_number = re.compile('(.*)        +[A-Z]?[1-9]+\.?',re.U)
end_number = re.compile('\s+[A-Z]?[1-9]+\.?\s+',re.U)
begin_number = re.compile('[1-9]+',re.U)
scene_number = re.compile('[A-Z]+[1-9]+(  +)',re.U)
space_context = re.compile('^ {1,9}',re.U)
dialog = re.compile('^ {1,9}([\w|-].*)',re.U)
parenthesis_dialog = re.compile('^  +(\(\w)',re.U)
blue_draft = re.compile('^ +BLUE DRAFT', re.U)
speaker = re.compile('^ +([A-Z])', re.U)
multiple_space = re.compile('  +', re.U)

#with open('Path/to/file', 'r') as content_file:
#    content = content_file.read()$
file1 = open("thor.txt", "r")
Lines = file1.readlines() 
New_lines = []
for index in range(len(Lines)):
    if not skip_line.match(Lines[index]) and not omitted.match(Lines[index]) and not blue_draft.match(Lines[index]) :
        Lines[index] = end_number.sub("\n", Lines[index])
        Lines[index] = scene_number.sub(r"  \1", Lines[index])
        Lines[index] = space_context.sub("", Lines[index])
        Lines[index] = dialog.sub(r'"\1"', Lines[index])
        Lines[index] = parenthesis_dialog.sub(r'\1', Lines[index])
        Lines[index] = speaker.sub(r'_\1', Lines[index])
        Lines[index] = multiple_space.sub(r' ', Lines[index])
        if begin_number.match(Lines[index]):
            Lines[index] = "\n" + Lines[index] + "\n"
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


file2 = open("thor2.txt", "w")
file2.writelines(New_lines)
file2.close()