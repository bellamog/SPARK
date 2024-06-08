###Originally socialDoors for RF1 Aging by Ori Zaff in 2022
###Edited for IMPACT by Billy Mitchell in 2023
from math import isnan, nan
from psychopy import visual, core, event, gui, data
from psychopy.visual import ShapeStim
import pandas as pd
import random
import os
import re
from datetime import datetime
import time

# ---------------------------------------------------
# ----- Variables You Might Want to Modify Later -----
# ---------------------------------------------------

# This denotes which monitor the task will show up on
MonitorUsed = 2
# This is a stylistic variable; just adds a little banner to make warnings easier to see in the terminal output
Warning = ' -------------- \n - ATTENTION: - \n -------------- \n '
# These commands catpure today's date and time and save it in a string format that can be included in the filename
now = datetime.now()
date = now.strftime("%Y-%m-%d_%H-%M")
ITIDUR_START = 1.0
Practice_Trials = 4

# ------------------------------
# ----- Setting up the GUI -----
# ------------------------------
## Denoting the task title
subjDlg = gui.Dlg(title="Feedback Games")                                 
## Denoting the Subject ID
subjDlg.addField('Enter Subject ID: ')                                  
## Denoting where we want the task to start
subjDlg.addField('Task:', choices=[' ',                   
                                   'E',
                                   'R'])
## Denoting where we want the task to start
subjDlg.addField('Starting Point:', choices=[' ',
                                             'Run 1',                   
                                             'Run 2'])
## Denoting where we want the task to start
subjDlg.addField('Practice Task:', choices=[' ',
                                            'Practice',                   
                                            'NoPractice'])
# ## Denoting where we want the task to start
# subjDlg.addField('Seed: ', random.randint(0, 9999))

# Present the GUI
subjDlg.show()
if subjDlg.OK == False:
    core.quit()

# Store values from the GUI as variables
## Storing Subject ID
subj_id = subjDlg.data[0]
## Storing Task Start
if subjDlg.data[1] == "E":
    task_type = "Encoding"
elif subjDlg.data[1] == "R":
    task_type = "Recall" 
else:      
    # If the operator forgets to select where to start the task, remind them                                                             
    print(Warning + 'You have not chosen which task to run (Encoding, or Recall). \n Please try again!')
    core.quit()
## Storing Task Start
if subjDlg.data[2] != " ":
    task_start = subjDlg.data[2]
else:      
    # If the operator forgets to select where to start the task, remind them                                                             
    print(Warning + 'You have not chosen where to start the task (run 1 or run 2). \n Please try again!')
    core.quit()
## Storing Task Start
if subjDlg.data[3] != " ":
    run_practice = subjDlg.data[3]
else:      
    # If the operator forgets to select where to start the task, remind them                                                             
    print(Warning + 'You have not chosen whether to include practice trials or not. \n Please try again!')
    core.quit()

# Determining Version Based upon PID
if subj_id[-1].isnumeric():

    ## If the final character of the PID is between 0 and 4, set the version to A
    ## For recall, version A means Recall on the left and Predict on the right
    ## Odd last characters see the 'faces' condition first, while even characters see the 'doors' condition first.
    if int(subj_id[-1]) < 5 and (int(subj_id[-1]) % 2) == 0:                                 
        version = 'A'
        condition = 'doors'
    elif int(subj_id[-1]) < 5 and (int(subj_id[-1]) % 2) != 0:                                 
        version = 'A'
        condition = 'faces'    
    ## If the final character of the PID is between 5 and 9, set the version to B    
    ## For recall, version B means Predict on the left and Recall on the right
    ## Odd last characters see the 'faces' condition first, while even characters see the 'doors' condition first.
    elif int(subj_id[-1]) > 4 and (int(subj_id[-1]) % 2) == 0:                                 
        version = 'B'
        condition = 'doors'
    elif int(subj_id[-1]) > 4 and (int(subj_id[-1]) % 2) != 0:                                 
        version = 'B'
        condition = 'faces'
    ## Otherwise, see version A and doors first
    else:
        version = 'A'
        condition = 'doors'

## If the final character of the PID does not fit either condition, print an error an exit the program.
else:                                                                   
    print(Warning + 'The subject ID you entered, ' + subj_id + ', does not seem to be in the appropriate format. \n The final character is not a numeric value. Please try again!')
    core.quit()

## Print the version that participants will see
print("Participant " + subj_id + " will complete version " + version +" of the task and see " + condition + " first!")

def extract_numeric_substrings(input_string):
    return re.findall(r'\d+', input_string)

def convert_to_numeric_objects(numeric_substrings):
    numeric_objects = []
    for substring in numeric_substrings:
        try:
            numeric_value = int(substring)  # Convert to int
        except ValueError:
            try:
                numeric_value = float(substring)  # If it's a floating-point number
            except ValueError:
                # Handle cases where substring couldn't be converted to int or float
                # You can decide what to do in such cases, e.g., skipping the value or handling it differently.
                continue

        numeric_objects.append(numeric_value)

    return numeric_objects

numeric_substrings = extract_numeric_substrings(subj_id)
numeric_objects = convert_to_numeric_objects(numeric_substrings)
random.seed(int(numeric_objects[0]))

# -----------------------------------------
# ----- Task Stage-Specific Variables -----
# -----------------------------------------

# I learned too late that the mock scanner doesn't use the same button response system that the scanner does; it's actually registering button presses as keypad presses. This is a problem because pressing '1' on the keypad isn't read as '1' in python; it's read as 'num_1'. We also don't need the keypad for every task, only for the practice encoding task. So I think the cleanest way to make this adjustment is to create new variables for each of the key presses and have their values be conditional upon whichever type of task we are running. 

# While the encoding and recall task use many of the same objects and variables, their sizes, positions and values change a little

if task_type == 'Encoding':
    ## Noting which keys the computer should look out for during the task because they do things
    responseKeys=['num_7', 'num_2', '7','2','z']
    BorderWidth = 0.2
    FBWidth = 20
    feedback_size = [0.4, 0.6]

if task_type == 'Recall':
    ## Noting which keys the computer should look out for during the task because they do things
    responseKeys=['num_9', '9', 'num_8', '8', 'num_7', '7', 'num_2', '2', 'num_3', '3', 'num_4', '4','z']
    FBWidth = 10
    ChoiceWidth = 20
    feedback_size = [0.2, 0.3]
    neutralfeedback_size = [0.18, 0.28]
    FB_Y = .8  
    FB_X1 = .8
    FB_X2 = .575
    FB_X3 = .35  

# ------------------------------------------------------------------
# ----- Creating Background Stimuli, Objects, and Dictionaries -----
# ------------------------------------------------------------------

## Loading .csv containing Trial, ITI, win or lose, and image and face ordering, set window, response keys information
reference = pd.read_csv((f'reference_{task_type}.csv'), header = 0)                  
## Loading Instructions
instructions = pd.read_excel((f'instructions.xlsx'), 
                             header = 0)                  

## Setting screen information
win = visual.Window(fullscr=True, allowGUI=False, screen=MonitorUsed, units="norm")

# Get the screen dimensions
screen_width = 2.15
screen_height = 2

if task_type == 'Encoding':
    # Calculate frame dimensions
    top_frame_dim = (screen_width, BorderWidth)
    bottom_frame_dim = (screen_width, BorderWidth)
    left_frame_dim = (BorderWidth, screen_height)
    right_frame_dim = (BorderWidth, screen_height)

## Creating stimuli to appear as fixation crosses and task feedback
isi = visual.TextStim(win, text="+", height=0.2)

## Creating visual objects (i.e., shapes, texts) as needed for each of the different task types 
if task_type == 'Encoding':
    no_resp = visual.TextStim(win, text="Please respond faster", pos = (0,0), wrapWidth=1.6, height= 0.08)
    feedback_positive = visual.Circle(win, size = feedback_size, edges = 200, lineWidth = FBWidth, lineColor = "lime", fillColor = "lime")
    feedback_negative = visual.Circle(win, size = feedback_size, edges = 200, lineWidth = FBWidth, lineColor = "darkred", fillColor = "darkred")
    feedback_neutral = visual.Circle(win, size = feedback_size, edges = 200, lineWidth = FBWidth, lineColor = "white", fillColor = "")
    top_frame_loss = visual.Rect(win, width=top_frame_dim[0], height=top_frame_dim[1], pos=(0, screen_height/2-BorderWidth/2), fillColor='darkred')
    bottom_frame_loss = visual.Rect(win, width=bottom_frame_dim[0], height=bottom_frame_dim[1], pos=(0, -screen_height/2+BorderWidth/2), fillColor='darkred')
    left_frame_loss = visual.Rect(win, width=left_frame_dim[0], height=left_frame_dim[1], pos=(-screen_width/2+BorderWidth/2, 0), fillColor='darkred')
    right_frame_loss = visual.Rect(win, width=right_frame_dim[0], height=right_frame_dim[1], pos=(screen_width/2-BorderWidth/2, 0), fillColor='darkred')
    top_frame_win = visual.Rect(win, width=top_frame_dim[0], height=top_frame_dim[1], pos=(0, screen_height/2-BorderWidth/2), fillColor='lime')
    bottom_frame_win = visual.Rect(win, width=bottom_frame_dim[0], height=bottom_frame_dim[1], pos=(0, -screen_height/2+BorderWidth/2), fillColor='lime')
    left_frame_win = visual.Rect(win, width=left_frame_dim[0], height=left_frame_dim[1], pos=(-screen_width/2+BorderWidth/2, 0), fillColor='lime')
    right_frame_win = visual.Rect(win, width=right_frame_dim[0], height=right_frame_dim[1], pos=(screen_width/2-BorderWidth/2, 0), fillColor='lime')

elif task_type == 'Recall':
    feedback_positive_L = visual.Circle(win, size = feedback_size, pos = (-FB_X1,-FB_Y), edges = 200, lineWidth = FBWidth, lineColor = "lime", fillColor = "lime")
    choice_win_L = visual.Circle(win, size = feedback_size, pos = (-FB_X1,-FB_Y), edges = 200, lineWidth = ChoiceWidth, lineColor = "white", fillColor = "lime")
    feedback_negative_L = visual.Circle(win, size = feedback_size, pos = (-FB_X2,-FB_Y), edges = 200, lineWidth = FBWidth, lineColor = "darkred", fillColor = "darkred")
    choice_loss_L = visual.Circle(win, size = feedback_size, pos = (-FB_X2,-FB_Y), edges = 200, lineWidth = ChoiceWidth, lineColor = "white", fillColor = "darkred")
    feedback_neutral_L = visual.Circle(win, size = neutralfeedback_size, pos = (-FB_X3,-FB_Y), edges = 200, lineWidth = FBWidth, lineColor = "white", fillColor = "")
    choice_neutral_L = visual.Circle(win, size = feedback_size, pos = (-FB_X3,-FB_Y), edges = 200, lineWidth = ChoiceWidth, lineColor = "white", fillColor = "")
    feedback_positive_R = visual.Circle(win, size = feedback_size, pos = (FB_X3,-FB_Y), edges = 200, lineWidth = FBWidth, lineColor = "lime", fillColor = "lime")
    choice_win_R = visual.Circle(win, size = feedback_size, pos = (FB_X3,-FB_Y), edges = 200, lineWidth = ChoiceWidth, lineColor = "white", fillColor = "lime")
    feedback_negative_R = visual.Circle(win, size = feedback_size, pos = (FB_X2,-FB_Y), edges = 200, lineWidth = FBWidth, lineColor = "darkred", fillColor = "darkred")
    choice_loss_R = visual.Circle(win, size = feedback_size, pos = (FB_X2,-FB_Y), edges = 200, lineWidth = ChoiceWidth, lineColor = "white", fillColor = "darkred")
    feedback_neutral_R = visual.Circle(win, size = neutralfeedback_size, pos = (FB_X1,-FB_Y), edges = 200, lineWidth = FBWidth, lineColor = "white", fillColor = "")    
    choice_neutral_R = visual.Circle(win, size = feedback_size, pos = (FB_X1,-FB_Y), edges = 200, lineWidth = ChoiceWidth, lineColor = "white", fillColor = "")     
    if version == "A":                                 
        text_left = visual.TextStim(win, text="Recall", pos = (-FB_X2,-.55), wrapWidth=1.6, height= 0.12)
        text_right = visual.TextStim(win, text="Predict", pos = (FB_X2,-.55), wrapWidth=1.6, height= 0.12)
    elif version == "B":                                 
        text_right = visual.TextStim(win, text="Recall", pos = (FB_X2,-.55), wrapWidth=1.6, height= 0.12)
        text_left = visual.TextStim(win, text="Predict", pos = (-FB_X2,-.55), wrapWidth=1.6, height= 0.12)

# ------------------------------
# ----- Defining Functions -----
# ------------------------------

## This function will have python commit to doing an entire run of the study. We feed it arguments for which stimset we want, which version we want, and which run (order) it is
def do_run(stimset, vers, run):

    ## Adding the proper titles that Camille asked for these tasks
    if stimset == 'doors':
        domain = 'monetary'
    else:
        domain = 'social'

    ## If we're on the 'recall' task' and not practicing... 
    if task_type == 'Recall' and vers != 'practice':
        ## Finding how many rows are present in our reference document for stimuli specifically
        indices_stims = list(range(reference.shape[0]))
        ## Shuffle those row indices randomly
        random.shuffle(indices_stims)
        ## Finding how many rows are present in our reference document for ISI's specifically
        indices_ISI = list(range(reference.shape[0]))
        ## Shuffle those row indices randomly
        random.shuffle(indices_ISI)
    ## If we're on the 'recall' task' and practicing, don't randomize anything. 
    elif task_type == 'Recall'and vers == 'practice':
        indices_stims = list(range(Practice_Trials))
        indices_ISI = list(range(Practice_Trials))
    ## If we're encoding, don't randomize anything. 
    elif task_type == 'Encoding' and vers != 'practice':
        indices_stims = list(range(reference.shape[0]))
        indices_ISI = list(range(reference.shape[0]))
        indices_FB = list(range(reference.shape[0]))
        indices_ITI = list(range(reference.shape[0]))
    elif task_type == 'Encoding' and vers == 'practice':
        indices_stims = list(range(Practice_Trials))
        indices_ISI = list(range(Practice_Trials))
        indices_FB = list(range(Practice_Trials))
        indices_ITI = list(range(Practice_Trials))


    #set Version ITI, Image orders, feedback order
    pic_path = os.path.join(os.getcwd(), 'pictureFolder', f'{stimset}Labelled',)

    ## Preload all of the images, ISIs, ITIs for this trial
    if task_type == "Encoding":
        pic_L_image_name = reference.loc[reference.index[indices_stims], f'{vers}_{stimset}_L']
        pic_R_image_name = reference.loc[reference.index[indices_stims], f'{vers}_{stimset}_R']
        pic_L_image_list = [os.path.join(pic_path, pic_name) for pic_name in pic_L_image_name]
        pic_R_image_list = [os.path.join(pic_path, pic_name) for pic_name in pic_R_image_name]
        pic_L_list = [visual.ImageStim(win,
                                 img, 
                                 pos =(-0.3,0), 
                                 size=(0.4,0.85)) for img in pic_L_image_list]
        pic_R_list = [visual.ImageStim(win,
                                 img, 
                                 pos =(0.3,0), 
                                 size=(0.4,0.85)) for img in pic_R_image_list]
        list_isi = reference.loc[reference.index[indices_ISI], f'{vers}_ISI']
        list_iti = reference.loc[reference.index[indices_ITI], f'{vers}_ITI']
        ## How long the feedback is visible for 
        dur_feedback = 1.0
        pic_R_type = reference.loc[reference.index[indices_stims], f'{vers}_{stimset}_R_type']
        pic_L_type = reference.loc[reference.index[indices_stims], f'{vers}_{stimset}_L_type']
        trial_type = reference.loc[reference.index[indices_stims], f'{vers}_trialtype']
    elif task_type == "Recall" and vers == "practice":
        pic_image_name = reference.loc[reference.index[indices_stims], f'{vers}_{stimset}']
        pic_image_list = [os.path.join(pic_path, pic_name) for pic_name in pic_image_name]
        pic_list = [visual.ImageStim(win,
                               img, 
                               pos =(0,0), 
                               size=(0.4,0.85)) for img in pic_image_list]
        list_isi = reference.loc[reference.index[indices_ISI], f'{vers}_isi']
        pic_type = reference.loc[reference.index[indices_stims], f'{vers}_{stimset}_type']
    elif task_type == "Recall" and vers != "practice":
        pic_image_name = reference.loc[reference.index[indices_stims], f'{stimset}']
        pic_image_list = [os.path.join(pic_path, pic_name) for pic_name in pic_image_name]
        pic_list = [visual.ImageStim(win,
                               img, 
                               pos =(0,0), 
                               size=(0.4,0.85)) for img in pic_image_list]
        list_isi = reference.loc[reference.index[indices_ISI], f'isi']
        pic_type = reference.loc[reference.index[indices_stims], f'{stimset}_type']

    ## Iterate sequentially through each row of the instructions file
    for instr in instructions.iterrows():

        ## Create a variable called row_counter which captures the index of the instruction that we're currently iterating through
        row_counter = instr[0]
        ## If a practice run, use the text from the relevant practice column in the instructions dataframe
        if run_practice == "Practice" and vers == "practice":
            if task_type == "Encoding":
                text = instructions.loc[instructions.index[row_counter], f'{task_type}_{stimset}_Practice']
                if pd.isna(instructions.loc[instructions.index[row_counter], f'{task_type}_{stimset}_Practice']):
                    break
            if task_type == "Recall":
                text = instructions.loc[instructions.index[row_counter], f'{task_type}_{stimset}_Practice_{version}']
                if pd.isna(instructions.loc[instructions.index[row_counter], f'{task_type}_{stimset}_Practice_{version}']):
                    break
        ## If not a practice run, use the text from the relevant non-practice column in the instructions dataframe
        else:
            if task_type == "Encoding":
                text = instructions.loc[instructions.index[row_counter], f'{task_type}_{stimset}_NoPractice']
                if pd.isna(instructions.loc[instructions.index[row_counter], f'{task_type}_{stimset}_NoPractice']):
                    break
            if task_type == "Recall":
                text = instructions.loc[instructions.index[row_counter], f'{task_type}_{stimset}_NoPractice_{version}']
                if pd.isna(instructions.loc[instructions.index[row_counter], f'{task_type}_{stimset}_NoPractice_{version}']):
                    break

         # Check if an image placeholder exists and split the text accordingly
        match = re.search(r"\{(.*?)\}", text)

        # If an image path was identified:           
        if match != None:

            # Split text around the image placeholder
            before_image_text = text[:match.start()]
            after_image_text = text[match.end():]
            image_path = match.group(1)

            ## Create a textstim & ImageStim containing the text we just pulled in
            text_stim_upper = visual.TextStim(win, text= before_image_text, pos = (0, 0.7), wrapWidth=1.6, height = 0.07) 
            text_stim_lower = visual.TextStim(win, text= after_image_text, pos=(0.0, -0.5), wrapWidth=1.75, height = 0.07)
            image_stim = visual.ImageStim(win, image = image_path, pos = (0.0, 0.2), size = (0.9, 0.9))
            border_width = 0.02
            image_border = visual.Rect(win, lineWidth=0, fillColor='white', width = image_stim.size[0] + 2 * border_width, height=image_stim.size[1] + 2 * border_width, pos= image_stim.pos)
 

        else:
            ## Create a textstim containing the text we just pulled in
            text_stim = visual.TextStim(win, text=text, pos = (0,0), wrapWidth=1.6, height = 0.08)
        
        ## Continuous Loop
        while True:    
            if match != None:      
                ## Draw that textstim on the screen
                image_border.draw()
                image_stim.draw()
                text_stim_upper.draw()
                text_stim_lower.draw()
            else: 
                 ## Draw that textstim on the screen
                text_stim.draw()
            win.flip()
            # Search for key presses
            resp = event.getKeys(keyList = ['z', '7', '2', '8', '3', 'num_7', 'num_2', 'num_8', 'num_3', 'space', 'equal'])
            # If z i pressed ...
            if 'z' in resp:
                # End the program                            
                core.quit()
            ## If this is the first instruction given
            if row_counter == 0:  
                if 'space' in resp:
                    # Break the while loop
                    break
            ## For all other instruction types, make participants cycle through the left index finger ...
            if row_counter % 4 == 1:  
                if 'num_7' in resp or '7' in resp:
                    # Break the while loop
                    break
            ## ... right pointer finger
            if row_counter % 4 == 2:  
                if 'num_2' in resp or '2' in resp:
                    # Break the while loop
                    break
            ## ... left middle finger
            if row_counter % 4 == 3:  
                if 'num_8' in resp or '8' in resp:
                    # Break the while loop
                    break
            ## ... right middle finger
            if row_counter % 4 == 0 & row_counter > 0:
                if 'num_3' in resp or '3' in resp:
                    # Break the while loop
                    break
    
    ## Generating a trigger screen ...
    if vers == "practice":
        text_stim = visual.TextStim(win, text="Please wait for the practice game to begin! \n\nRemember to keep your head still and respond quickly!", pos = (0,0), wrapWidth=1.6, height = 0.08)
    else:
        text_stim = visual.TextStim(win, text="Please wait for the game to begin! \n\nRemember to keep your head still and respond quickly!!", pos = (0,0), wrapWidth=1.6, height = 0.08)
    
    # Creating another continuous while loop
    while True: 
        ## Draw that textstim on the screen
        text_stim.draw()
        win.flip()
        # Search for key presses
        resp = event.getKeys(keyList = ['equal', 'space', 'z'])
        # If z i pressed ...
        if 'z' in resp:
            # End the program                            
            core.quit() 
        # If this is a practice version
        if vers == "practice":
            ## Once space is pressed, start the task
            if 'space' in resp:
                # Break the while loop
                break
        else: 
            ## Once the trigger (=) is sent, start the task
            if 'equal' in resp:
                # Break the while loop
                break
    
    ## Start keeping track of the timing for this run
    run_start = time.time()
    
    ## How long participants have to make their decision
    if task_type == 'Encoding':
        dur_decision = 2.5
    elif task_type == "Recall":
        dur_decision = 2.75
    
    ## Lists to store logging
    clock = core.Clock()
    clock.reset()
    b_1 = []
    b_2 = []
    b_3 = []
    b_4 = []
    b_5 = []
    b_6 = []
    b_7 = []
    b_8 = []
    b_9 = []
    if task_type == 'Encoding':
        b_10 = []
        b_11 = []

    #hide mouse
    win.mouseVisible = False

    ## Draw an initial ISI that lasts for 5 seconds
    isi.draw()
    win.flip()
    core.wait(ITIDUR_START)

    ## Log that initial ISI in out new lists
    b_1.append(0)
    b_2.append(ITIDUR_START)
    if task_type == "Encoding":    
        b_3.append('ITI')
    else:    
        b_3.append('ISI')    
    b_4.append('n/a')
    b_5.append('n/a')
    b_6.append('n/a')
    b_7.append('n/a')
    if task_type == "Encoding":
        b_8.append('n/a')
        b_9.append('n/a')
        b_10.append('n/a')
        b_11.append('n/a')  
    elif task_type == "Recall":
        b_8.append('n/a')
        b_9.append('n/a')  

    # ------------------
    # ----- Trials -----
    # ------------------ 
    ## Iterate through the trials 
    for trial in reference.iterrows():
        ## Iterate through the trials sequentially
        row_counter = trial[0] 
        ## If this is a practice session and we reach the third iteration, stop the task
        if vers == 'practice' and row_counter > (Practice_Trials - 1):
            print('Practice Complete')
            break
        ## Generate task specific objects such as stimuli, borders, ITI and ISI durations
        if task_type == "Encoding":
            pic_R = pic_R_list[row_counter]
            pic_L = pic_L_list[row_counter]
            dur_isi = list_isi[row_counter]
            dur_iti = list_iti[row_counter]
            trial_timer = core.CountdownTimer(dur_decision + dur_isi + dur_feedback + dur_iti)
            border = visual.ShapeStim(win, vertices=pic_L.verticesPix, units='pix', fillColor = 'grey', lineColor = 'grey')
            border2 = visual.ShapeStim(win, vertices=pic_R.verticesPix, units='pix', fillColor = 'grey', lineColor = 'grey')
            select_2 = visual.ShapeStim(win, vertices=pic_L.verticesPix, units='pix', lineWidth = 10, lineColor = 'white')
            select_3 = visual.ShapeStim(win, vertices=pic_R.verticesPix, units='pix', lineWidth = 10, lineColor = 'white')            
        elif task_type == "Recall" and vers == "practice":
            pic = pic_list[row_counter]
            dur_isi = list_isi[row_counter]
            trial_timer = core.CountdownTimer(dur_isi + dur_decision)
            border = visual.ShapeStim(win, vertices=pic.verticesPix, units='pix', fillColor = 'grey', lineColor = 'grey')
        elif task_type == "Recall" and vers != "practice":
            pic = pic_list[row_counter]
            dur_isi = list_isi.iloc[[row_counter]].values[0]
            trial_timer = core.CountdownTimer(dur_isi + dur_decision)          
            border = visual.ShapeStim(win, vertices=pic.verticesPix, units='pix', fillColor = 'grey', lineColor = 'grey')       

        ## While there's still time on the trial clock, do the following
        while trial_timer.getTime() > 0:
            # --------------------
            # ----- Decision -----
            # --------------------   
            ## Start a countdown timer according to the duration of this event
            timer = core.CountdownTimer(dur_decision)
            ## Look for keys that we put on our response list
            resp = event.getKeys(keyList = responseKeys)
            ## Get the time when this event starts
            decision_onset = clock.getTime()
            ## Pulling frame and stimulus information from the reference document                  
            if task_type == "Encoding":
                if trial_type[row_counter] == 'win':
                    top_frame = top_frame_win
                    bottom_frame = bottom_frame_win
                    left_frame = left_frame_win
                    right_frame = right_frame_win
                else:
                    top_frame = top_frame_loss
                    bottom_frame = bottom_frame_loss
                    left_frame = left_frame_loss
                    right_frame = right_frame_loss
            ## While the timer for this event is still counting, do the following
            while timer.getTime() > 0:
                ## Draw task-specific objects (i.e., text, frames, pictures, etc.)
                if task_type == "Encoding":
                    pic_L.draw()
                    pic_R.draw()
                    top_frame.draw()
                    bottom_frame.draw()
                    left_frame.draw()
                    right_frame.draw()
                elif task_type == "Recall":
                    pic.draw()
                    feedback_positive_L.draw()
                    feedback_negative_L.draw()
                    feedback_neutral_L.draw()
                    feedback_positive_R.draw()
                    feedback_negative_R.draw()
                    feedback_neutral_R.draw()
                    text_left.draw()
                    text_right.draw()
                win.flip()
                ## Accept keys on the response key list
                resp = event.getKeys(keyList = responseKeys)
                ## If a key from that list is pressed ...
                if len(resp) > 0:
                    ## ... and it's a z ...
                    if 'z' in resp:
                        if task_type == "Recall" and vers != "practice":                
                            ## ... quit the task and save our current progress as a .csv 
                            bidsEvents.to_csv(os.path.join("data",subj_id, f"sub-{subj_id}_{task_type}_{domain}_run{run}_{date}.tsv"), sep='\t', index = False) 
                        else:                
                            ## ... quit the task and save our current progress as a .csv 
                            bidsEvents.to_csv(os.path.join("data",subj_id, f"sub-{subj_id}_{task_type}_{domain}_run{run}_{vers}_{date}.tsv"), sep='\t', index = False)                             
                        core.quit()
                    ## If it's an encoding task, record the responses, draw the frames that people select
                    if task_type == "Encoding":
                        if selected == 7 or 2:
                            # If the keypad was used, remove the "num_" prefix from the response
                            if resp[0].startswith("num_"):
                                resp[0] = resp[0][4:]
                            selected = int(resp[0])
                            if selected == 7:
                                pic_L.draw()
                                pic_R.draw()
                                top_frame.draw()
                                bottom_frame.draw()
                                left_frame.draw()
                                right_frame.draw()
                                l_r = 'left'
                                select_2.draw()
                                win.flip()
                                core.wait(.01)
                            elif selected == 2:
                                pic_R.draw()
                                pic_L.draw()
                                top_frame.draw()
                                bottom_frame.draw()
                                left_frame.draw()
                                right_frame.draw()
                                l_r = 'right'
                                select_3.draw()
                                win.flip()
                                core.wait(.01)
                            ## Get the time at which the response was recorded
                            resp_onset = clock.getTime()
                            ## Calculate the response time 
                            rt = resp_onset - decision_onset
                            ## Redraw relevant objects
                            border.autoDraw=True
                            border2.autoDraw=True
                            pic_L.draw()
                            pic_R.draw()
                            ## Wait the rest of the time for this event
                            core.wait(dur_decision - rt)
                            break
                    ## If it's a recall task, pretty much do the same thing I listed for encoding with a new set of objects 
                    elif task_type == "Recall":
                        if selected == 9 or 8 or 7 or 2 or 3 or 4:
                            # If the keypad was used, remove the "num_" prefix from the response
                            if resp[0].startswith("num_"):
                                resp[0] = resp[0][4:]
                            selected = int(resp[0])
                            if selected == 9:
                                pic.draw()
                                feedback_positive_L.draw()
                                feedback_negative_L.draw()
                                feedback_neutral_L.draw()
                                feedback_positive_R.draw()
                                feedback_negative_R.draw()
                                feedback_neutral_R.draw()
                                text_left.draw()
                                text_right.draw()
                                fb_pic_R_type = 'win'
                                if version == "A":
                                    fb_cat_resp = 'recall'
                                elif version == "B": 
                                    fb_cat_resp = 'predict'
                                choice_win_L.draw()
                                win.flip()
                                core.wait(.01)
                            elif selected == 8:
                                pic.draw()
                                feedback_positive_L.draw()
                                feedback_negative_L.draw()
                                feedback_neutral_L.draw()
                                feedback_positive_R.draw()
                                feedback_negative_R.draw()
                                feedback_neutral_R.draw()
                                text_left.draw()
                                text_right.draw()
                                fb_pic_R_type = 'loss'
                                if version == "A":
                                    fb_cat_resp = 'recall'
                                elif version == "B": 
                                    fb_cat_resp = 'predict'
                                choice_loss_L.draw()
                                win.flip()
                                core.wait(.01)    
                            elif selected == 7:
                                pic.draw()
                                feedback_positive_L.draw()
                                feedback_negative_L.draw()
                                feedback_neutral_L.draw()
                                feedback_positive_R.draw()
                                feedback_negative_R.draw()
                                feedback_neutral_R.draw()
                                text_left.draw()
                                text_right.draw()
                                fb_pic_R_type = 'neutral'
                                if version == "A":
                                    fb_cat_resp = 'recall'
                                elif version == "B": 
                                    fb_cat_resp = 'predict'
                                choice_neutral_L.draw()
                                win.flip()
                                core.wait(.01)    
                            elif selected == 2:
                                pic.draw()
                                feedback_positive_L.draw()
                                feedback_negative_L.draw()
                                feedback_neutral_L.draw()
                                feedback_positive_R.draw()
                                feedback_negative_R.draw()
                                feedback_neutral_R.draw()
                                text_left.draw()
                                text_right.draw()
                                fb_pic_R_type = 'win'
                                if version == "B":
                                    fb_cat_resp = 'recall'
                                elif version == "A": 
                                    fb_cat_resp = 'predict'
                                choice_win_R.draw()
                                win.flip()
                                core.wait(.01)
                            elif selected == 3:
                                pic.draw()
                                feedback_positive_L.draw()
                                feedback_negative_L.draw()
                                feedback_neutral_L.draw()
                                feedback_positive_R.draw()
                                feedback_negative_R.draw()
                                feedback_neutral_R.draw()
                                text_left.draw()
                                text_right.draw()
                                fb_pic_R_type = 'loss'
                                if version == "B":
                                    fb_cat_resp = 'recall'
                                elif version == "A": 
                                    fb_cat_resp = 'predict'
                                choice_loss_R.draw()
                                win.flip()
                                core.wait(.01)
                            elif selected == 4:
                                pic.draw()
                                feedback_positive_L.draw()
                                feedback_negative_L.draw()
                                feedback_neutral_L.draw()
                                feedback_positive_R.draw()
                                feedback_negative_R.draw()
                                feedback_neutral_R.draw()
                                text_left.draw()
                                text_right.draw()
                                fb_pic_R_type = 'neutral'
                                if version == "B":
                                    fb_cat_resp = 'recall'
                                elif version == "A": 
                                    fb_cat_resp = 'predict'
                                choice_neutral_R.draw()
                                win.flip()
                                core.wait(.01)           
                        ## Get the time at which the response occurred                                                                                                                        
                        resp_onset = clock.getTime()
                        ## Calculate the response time of the response
                        rt = resp_onset - decision_onset
                        ## Redraw all relevant objects and wait for the clock to run out for this event
                        border.autoDraw=True
                        pic.draw()
                        core.wait(dur_decision - rt)
                        break
                # If no response was given, consider this event missed
                else:
                    resp = 'missed'
                    selected = 'missed'
                    rt = 'missed'
            decision_eventtime = clock.getTime() - decision_onset 
            border.autoDraw=False
            ## Capture the gender of the stimulus
            if task_type == "Encoding":
                border2.autoDraw=False
                gender = (pic_path, reference.loc[reference.index[indices_stims[row_counter]], f'{vers}_{stimset}_L'])
            elif task_type == "Recall" and vers == "practice":
                gender = (pic_path, reference.loc[reference.index[indices_stims[row_counter]], f'{vers}_{stimset}'])
            elif task_type == "Recall" and vers != "practice":
                gender = (pic_path, reference.loc[reference.index[indices_stims[row_counter]], f'{stimset}'])

            if rt == 'missed':
                selection = "missed"
            else:
                if task_type == "Encoding":
                    selection = l_r
                else:
                    selection = str(fb_cat_resp + "_" + fb_pic_R_type)

            ## Log the relevatn information for this event
            b_1.append(decision_onset)
            b_2.append(decision_eventtime)
            if rt == 'missed':
                if task_type == "Encoding":
                    b_3.append(f'decision_{domain}_{trial_type[row_counter]}_MISSED')
                else:
                    b_3.append(f'decision_{domain}_MISSED')
            else:
                if task_type == "Encoding":
                    b_3.append(f'decision_{domain}_{trial_type[row_counter]}')
                else:
                    b_3.append(f'decision_{domain}')
            b_4.append(rt)
            b_5.append(selected)
            b_6.append(selection)
            if gender[1][:2] != "L_":
                b_7.append(gender[1][:1])
            elif gender[1][:2] == "L_":
                b_7.append(gender[1][2:3])  
            if task_type == "Encoding":
                b_8.append(pic_L_image_name[row_counter])
                b_9.append(pic_R_image_name[row_counter])
                b_10.append(pic_L_type[row_counter])
                b_11.append(pic_R_type[row_counter])  
            elif task_type == "Recall":
                b_8.append(pic_image_name.iloc[[row_counter]].values[0])
                b_9.append(pic_type.iloc[[row_counter]].values[0]) 
            selection = 'n/a'          

            # -------------------
            # ----- ISI -----
            # -------------------
            timer = core.CountdownTimer(dur_isi)
            isi_resp = event.getKeys(keyList = responseKeys)
            isi_onset = clock.getTime()
            while timer.getTime() > 0:
                if task_type == "Recall":
                    isi.draw()
                win.flip()
                isi_resp = event.getKeys(keyList = responseKeys)
                if len(isi_resp) > 0:
                    if 'z' in isi_resp:
                        if task_type == "Recall" and vers != "practice":                
                            ## ... quit the task and save our current progress as a .csv 
                            bidsEvents.to_csv(os.path.join("data",subj_id, f"sub-{subj_id}_{task_type}_{domain}_run{run}_{date}.tsv"), sep='\t', index = False) 
                        else:                
                            ## ... quit the task and save our current progress as a .csv 
                            bidsEvents.to_csv(os.path.join("data",subj_id, f"sub-{subj_id}_{task_type}_{domain}_run{run}_{vers}_{date}.tsv"), sep='\t', index = False)   
                        core.quit()
                    else:
                        if resp[0].startswith("num_"):
                            resp[0] = resp[0][4:]
                        isi_selected = int(isi_resp[0])
                        if task_type == "Encoding":
                            if isi_selected == 7 or 2:
                                # If the keypad was used, remove the "num_" prefix from the response
                                if resp[0].startswith("num_"):
                                    resp[0] = resp[0][4:]    
                                isi_selected = int(isi_resp[0])
                                if isi_selected == 7:
                                    l_r = 'left'
                                elif selected == 2:
                                    l_r = 'right'
                            # isi.draw()
                            isi_rt = clock.getTime() - isi_onset
                            core.wait(dur_isi - isi_rt)
                        elif task_type == "Recall":
                            if isi_selected == 9 or 8 or 7 or 2 or 3 or 4:
                                # If the keypad was used, remove the "num_" prefix from the response
                                if resp[0].startswith("num_"):
                                    resp[0] = resp[0][4:]
                                isi_selected = int(isi_resp[0])
                                if isi_selected == 9:
                                    fb_pic_R_type = 'win'
                                    if version == "A":
                                        fb_cat_resp = 'recall'
                                    elif version == "B": 
                                        fb_cat_resp = 'predict'
                                elif isi_selected == 8:
                                    fb_pic_R_type = 'loss'
                                    if version == "A":
                                        fb_cat_resp = 'recall'
                                    elif version == "B": 
                                        fb_cat_resp = 'predict'
                                elif isi_selected == 7:
                                    pic.draw()
                                    fb_pic_R_type = 'neutral'
                                    if version == "A":
                                        fb_cat_resp = 'recall'
                                    elif version == "B": 
                                        fb_cat_resp = 'predict'   
                                elif isi_selected == 2:
                                    fb_pic_R_type = 'win'
                                    if version == "B":
                                        fb_cat_resp = 'recall'
                                    elif version == "A": 
                                        fb_cat_resp = 'predict'
                                elif isi_selected == 3:
                                    fb_pic_R_type = 'loss'
                                    if version == "B":
                                        fb_cat_resp = 'recall'
                                    elif version == "A": 
                                        fb_cat_resp = 'predict'
                                elif isi_selected == 4:
                                    fb_pic_R_type = 'neutral'
                                    if version == "B":
                                        fb_cat_resp = 'recall'
                                    elif version == "A": 
                                        fb_cat_resp = 'predict'
                            isi.draw()
                            isi_rt = clock.getTime() - isi_onset
                            core.wait(dur_isi - isi_rt)
                else:
                    isi_resp = 'n/a'
                    isi_selected = 'n/a'
                    isi_rt = 'n/a'
            isi_eventtime = clock.getTime() -isi_onset

            if isi_rt == 'n/a':
                isi_selection = "n/a"
            else:
                if task_type == "Encoding":
                    isi_selection = l_r
                else:
                    isi_selection = str(fb_cat_resp + "_" + fb_pic_R_type)

            # Logging
            b_1.append(isi_onset)
            b_2.append(isi_eventtime)
            b_3.append('ISI')
            b_4.append(isi_rt)
            b_5.append(isi_selected)
            b_6.append(isi_selection)
            if gender[1][:2] != "L_":
                b_7.append(gender[1][:1])
            elif gender[1][:2] == "L_":
                b_7.append(gender[1][2:3])    
            if task_type == "Encoding":
                b_8.append(pic_L_image_name[row_counter])
                b_9.append(pic_R_image_name[row_counter])
                b_10.append(pic_L_type[row_counter])
                b_11.append(pic_R_type[row_counter])  
            elif task_type == "Recall":
                b_8.append(pic_image_name.iloc[[row_counter]].values[0])
                b_9.append(pic_type.iloc[[row_counter]].values[0])   

            if task_type == "Encoding":
                # --------------------
                # ----- FEEDBACK -----
                # --------------------
                timer = core.CountdownTimer(dur_feedback)
                feedback_onset = clock.getTime()
                fb_type = reference.loc[reference.index[indices_FB[row_counter]], f'{vers}_feedback']
                if resp == 'missed':
                    while timer.getTime() > 0:
                        no_resp.draw()
                        win.flip()
                elif resp == 7 or 2:
                    if fb_type == 'negative': 
                        while timer.getTime() > 0:
                            feedback_negative.draw()
                            win.flip()
                    elif fb_type == 'positive':
                        while timer.getTime() > 0:
                            feedback_positive.draw()
                            win.flip() 
                    elif fb_type == 'neutral':
                        while timer.getTime() > 0:
                            feedback_neutral.draw()
                            win.flip() 
                    else:
                        print('Feedback Error')
                else:
                    print('Feedback Error')
                typefeedback_eventtime = clock.getTime() - feedback_onset
                
                # Logging
                b_1.append(feedback_onset)
                b_2.append(typefeedback_eventtime)
                if resp == 'missed':
                    b_3.append(f'feedback_{domain}_{trial_type[row_counter]}_MISSED')
                else:
                    b_3.append(f'feedback_{domain}_{trial_type[row_counter]}_{fb_type}')
                b_4.append('n/a')
                b_5.append('n/a')
                b_6.append('n/a')
                if gender[1][:2] != "L_":
                    b_7.append(gender[1][:1])
                elif gender[1][:2] == "L_":
                    b_7.append(gender[1][2:3])  
                if task_type == "Encoding":
                    b_8.append(pic_L_image_name[row_counter])
                    b_9.append(pic_R_image_name[row_counter])
                    b_10.append(pic_L_type[row_counter])
                    b_11.append(pic_R_type[row_counter])  
                elif task_type == "Recall":
                    b_8.append(pic_image_name.iloc[[row_counter]].values[0])
                    b_9.append(pic_type.iloc[[row_counter]].values[0])  


                # ---------------
                # ----- ITI -----
                # ---------------
                timer = core.CountdownTimer(dur_iti)
                iti_resp = event.getKeys(keyList = responseKeys)
                iti_onset = clock.getTime()
                while timer.getTime() > 0:
                    isi.draw()
                    iti_resp = event.getKeys(keyList = responseKeys)
                    win.flip()
                    if len(iti_resp) > 0:
                        if 'z' in iti_resp:
                            bidsEvents.to_csv(os.path.join("data",subj_id, f"sub-{subj_id}_{task_type}_{domain}_run{run}_{vers}_{date}.tsv"), sep='\t', index = False) 
                            core.quit()
                iti_eventtime = clock.getTime() -iti_onset

                # Logging
                b_1.append(iti_onset)
                b_2.append(iti_eventtime)
                b_3.append('ITI')
                b_4.append('n/a')
                b_5.append('n/a')
                b_6.append('n/a')
                if gender[1][:2] != "L_":
                    b_7.append(gender[1][:1])
                elif gender[1][:2] == "L_":
                    b_7.append(gender[1][2:3])  
                if task_type == "Encoding":
                    b_8.append(pic_L_image_name[row_counter])
                    b_9.append(pic_R_image_name[row_counter])
                    b_10.append(pic_L_type[row_counter])
                    b_11.append(pic_R_type[row_counter])  
                elif task_type == "Recall":
                    b_8.append(pic_image_name.iloc[[row_counter]].values[0])
                    b_9.append(pic_type.iloc[[row_counter]].values[0])   

        ## Saving data to an appropriate BIDS format.  
        if task_type == "Encoding":
            bidsEvents = pd.DataFrame(
                    {'onset':b_1, 
                    'duration':b_2,
                    'trial_type':b_3,
                    'rt':b_4,
                    'resp':b_5,
                    'selection':b_6,
                    'gender':b_7,
                    'image_left':b_8,
                    'image_right':b_9,
                    'image_left_type':b_10,
                    'image_right_type':b_11})   
                   
        if task_type == "Recall":
            bidsEvents = pd.DataFrame(
                    {'onset':b_1, 
                    'duration':b_2,
                    'trial_type':b_3,
                    'rt':b_4,
                    'resp':b_5,
                    'selection':b_6,
                    'gender':b_7,
                    'image':b_8,
                    'image_type':b_9})
        
        ## Outputting that BIDS event as a .csv
        if task_type == "Recall" and vers != "practice":                
            bidsEvents.to_csv(os.path.join("data",subj_id, f"sub-{subj_id}_{task_type}_{domain}_run{run}_{date}.tsv"), sep='\t', index = False) 
        else:                
            bidsEvents.to_csv(os.path.join("data",subj_id, f"sub-{subj_id}_{task_type}_{domain}_run{run}_{vers}_{date}.tsv"), sep='\t', index = False)   
      
    run_end = time.time()
    run_length = run_end -run_start
    print(run_length)
    event.clearEvents()
    return;

## Defining a function to run all of the runs in a particular order based upon the information entered into the dialogue box
## This is kind of superfluous, but it's how Caleb already had it so I left it untouched
def all_run():
    # Check if the directory exists
    if not os.path.exists('data'):
        # Create the directory
        os.makedirs('data')
    try:
        os.mkdir(f'data/{subj_id}')
    except:
        print(Warning + '-- Subject File Already Exists --')
    if task_type == "Encoding":
        # Old order of events (Practice run 1 and 2; or No Practice run 1 and 2)
        if run_practice == "NoPractice":
            if condition == 'faces':
                if task_start == 'Run 1':
                    do_run('faces', version, 1)
                    do_run('doors', version, 2)
                elif task_start == 'Run 2':
                    do_run('doors', version, 2)
            elif condition == 'doors':
                if task_start == 'Run 1':
                    do_run('doors', version, 1)
                    do_run('faces', version, 2)
                elif task_start == 'Run 2':
                    do_run('faces', version, 2)
        elif run_practice == "Practice":
            if condition == 'faces':
                if task_start == 'Run 1':
                    do_run('faces', 'practice', 1)
                    do_run('doors', 'practice', 2)
                if task_start == 'Run 2':
                    do_run('doors', 'practice', 2)
            if condition == 'doors':
                if task_start == 'Run 1':
                    do_run('doors', 'practice', 1)
                    do_run('faces', 'practice', 2)                
                if task_start == 'Run 2':
                    do_run('faces', 'practice', 2)
    elif task_type == "Recall":
        # New order of events (Practice for run 1 flows into NoPractice for run 1, etc.)
        if task_start == 'Run 1':
            if condition == 'faces':
                if run_practice == "Practice":
                    do_run('faces', 'practice', 1)
                do_run('faces', version, 1)
                if run_practice == "Practice":
                    do_run('doors', 'practice', 2)
                do_run('doors', version, 2)
            if condition == 'doors':
                if run_practice == "Practice":
                    do_run('doors', 'practice', 1)
                do_run('doors', version, 1)
                if run_practice == "Practice":
                    do_run('faces', 'practice', 2)
                do_run('faces', version, 2)
        if task_start == 'Run 2':
            if condition == 'faces':
                if run_practice == "Practice":
                    do_run('doors', 'practice', 2)
                do_run('doors', version, 2)
            if condition == 'doors':
                if run_practice == "Practice":
                    do_run('faces', 'practice', 2)
                do_run('faces', version, 2)

# ------------------------------
# ----- Executing the Task -----
# ------------------------------

## Running the task
all_run()
## Printing in the terminal
print('Task Completed')
## Creating a text complete object
text_complete = visual.TextStim(win, text="Task Complete", pos = (0,0), wrapWidth=1.6, height= 0.12)
## Showing the object
text_complete.draw()
win.flip()
## Waiting ten seconds before closing out 
core.wait(5.0)
core.quit()