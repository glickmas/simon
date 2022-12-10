# Seth Glickman
# GAME 235 - Final Project
# 12/09/22

# sound library, osc/env vars
add_library('sound')
attackTime = 0.001
sustainTime = 0.008
sustainLevel = 0.3
releaseTime = 0.4

# game state enum
INTRO_SCREEN = -1
LISTEN_STATE = 0
PLAY_STATE = 1
WRONG_STATE = 2
WIN_STATE = 3
gameState = -1

# mouse click logic
isReleased = False

# buttons (keys) on the simon machine
simonKeyCount = 4
simonKeys = []
KEY_WIDTH = 180
KEY_HEIGHT = 300
LEFT_EDGE = 20
GUTTER = 12
BOTTOM_EDGE = 20
RIGHT_EDGE = 20 # for text

SIMON_BLUE = color(38, 121, 255)
SIMON_RED = color(255, 38, 38)
SIMON_GREEN = color(38, 255, 92)
SIMON_YELLOW = color(233, 255, 38)
colors = [SIMON_YELLOW, SIMON_BLUE, SIMON_RED, SIMON_GREEN]

# spliced for each round
seq = []

# collects user input
userPlayed = []

# lists, variable, defaults for playback 
seqLength = 1
seqIndex = 0
REST_AMOUNT = 50

pitches = []
sequence = []

songCount = 4
songNumber = -1 # -1 is used as default to ensure same song isn't played twice in a row

# delay before restart
gameOverTimer = 0

# start button
START_BTN_COLOR = color(240)
START_BTN_WIDTH = 200
START_BTN_HEIGHT = 70

def setup():
    global osc, env, songNumber, startButton
    size(800, 400)

    # prepare start button
    startBtnPos = PVector(width/2, height/2)
    startButton = UIButton(startBtnPos, START_BTN_COLOR, START_BTN_WIDTH, START_BTN_HEIGHT)
    startButton.assignText("START")
    
    # prepare oscillator and envelope
    osc = SinOsc(this) # SqrOsc, TriOsc, SawOsc, SinOsc, Pulse
    env = Env(this)
    
    # randomly choose a song
    selectSong(songNumber)
                        
    # create a list with pos, col, and pitch for Simon Keys 
    buildSimonKeyList()
    
    # assign pitches to the simon keys (buttons)
    assignPitches()
    
def draw():
    background(0)
    global gameState, seq, gameOverTimer
    
    resetKeys()
    
    
    ###############################################
    # LISTEN - user listens to the system play
    ###############################################
    
    if gameState == LISTEN_STATE:
        global sequence, seqIndex, seqLength
        
        # separate note playback
        if frameCount % REST_AMOUNT == 0:
            
            # get current sequence segment
            seq = prepareSequence(sequence, seqLength)
            
            # call trigger and light methods for each note in seq segment
            if seqIndex < len(seq):
                simonKeys[seq[seqIndex]].trigger()
                simonKeys[seq[seqIndex]].light()
                seqIndex += 1
            else:
                # lengthen the segment and reset the index
                if seqLength < len(sequence):
                    seqLength += 1
                    seqIndex = 0
                else:
                    # the segment is the entire sequence
                    # print("Done")
                    pass
                    
                gameState = PLAY_STATE


    ###############################################
    # PLAY - user plays back what they heard
    ###############################################
    
    elif gameState == PLAY_STATE: 
        
        # handle mouse interaction
        updateSimonKeys()
        
        # pattern matching logic
        evaluateUserPlayed()


    ###############################################
    # WRONG ANSWER - user plays a wrong note
    ###############################################
    
    elif gameState == WRONG_STATE:
        
        # display gameOver text for 2 seconds
        if gameOverTimer  < 120:
            fill(255)
            textSize(60)
            textAlign(CENTER)
            text("GAME OVER", width/2, height/2)
            gameOverTimer += 1
            
        # 0.5 second fade    
        elif gameOverTimer >= 120 and gameOverTimer < 150:
            _fadeOut = map(gameOverTimer, 120, 140, 255, 0)
            fill(_fadeOut)
            textSize(60)
            textAlign(CENTER)
            text("GAME OVER", width/2, height/2)
            gameOverTimer += 1
        
        # restart the game
        else:
            resetGame()
            selectSong(songNumber) # pass the current song number to avoid sequential duplicates
            assignPitches()
            
            gameState = LISTEN_STATE
            
            
    ###############################################
    # WIN - user plays the complete song
    ###############################################
    
    elif gameState == WIN_STATE:
        
        # win state animation
        if gameOverTimer < 25:
            for simonKey in simonKeys:
                simonKey.light()            
            gameOverTimer += 1            
        elif gameOverTimer >= 25 and gameOverTimer < 50:
            gameOverTimer += 1
        elif gameOverTimer >= 50 and gameOverTimer < 75:
            for simonKey in simonKeys:
                simonKey.light()
            gameOverTimer += 1
        elif gameOverTimer >= 75 and gameOverTimer < 100:
            gameOverTimer += 1
        elif gameOverTimer >= 100 and gameOverTimer < 125:
            for simonKey in simonKeys:
                simonKey.light()
            gameOverTimer += 1
        elif gameOverTimer >= 125 and gameOverTimer < 150:
            gameOverTimer += 1
            
        # restart game
        else:
            resetGame()
            selectSong(songNumber)
            assignPitches()
            
            gameState = LISTEN_STATE

    # in all states other than WRONG_STATE, display keys and title
    if gameState != WRONG_STATE:
        # display Simon Keys
        for i in range(len(simonKeys)):
            simonKeys[i].display()
            
        # display title
        fill(240)
        textSize(60)
        textAlign(LEFT)
        text("SIMON", LEFT_EDGE, 65)
        fill(128)
        text("CLASSIC", LEFT_EDGE + 210, 65)
        text("GAME", LEFT_EDGE + 460, 65)
        fill(220)
        textSize(15)
        text("redesigned by:", LEFT_EDGE + 650, 45)
        text("Seth Glickman", LEFT_EDGE + 650, 65) 
        
    # display the start button on top in INTRO_SCREEN state
    if gameState == INTRO_SCREEN:        
        startButton.update()
        startButton.display()

                        
# parent class
class Button:
    def __init__(self, pos, col, wid, hei):
        self.pos = pos
        self.col = col
        self.opa = 128
        self.wid = wid
        self.hei = hei
        
    def glow(self):
        self.opa = 150
        
    def light(self):
        self.opa = 255
        
    def reset(self):
        self.opa = 128
        
    def display(self):
        _col = color(self.col, self.opa)
        fill(_col)
        noStroke()
        rect(self.pos.x, self.pos.y, self.wid, self.hei)

# child class for start button
class UIButton(Button):
    def assignText(self, text):
        self.buttonText = text
        
    def display(self):
        # _col = color(self.col)
        fill(self.col)
        # noFill()
        # noStroke()
        stroke(255)
        rect(self.pos.x - self.wid/2, self.pos.y - self.hei/2, self.wid, self.hei)
        fill(0)
        textSize(40)
        textAlign(CENTER)
        text(self.buttonText, width/2, self.pos.y + self.hei/4)
        
    def update(self):
        global gameState        
        if mouseY > self.pos.y and mouseY < self.pos.y + START_BTN_HEIGHT:
            if mouseX > self.pos.x and mouseX < self.pos.x + START_BTN_WIDTH:
                self.glow()
                print("hover")
                if mousePressed:
                    print("click")
                    gameState = LISTEN_STATE
                    self.light()
                    
                else:
                    self.reset()
                    
            else:
                self.reset()

# child class for simon buttons (keys)
class SimonKey(Button):
    def trigger(self):
        osc.play()
        osc.freq(self.freq)
        env.play(osc, attackTime, sustainTime, sustainLevel, releaseTime)
    
    def assignPitch(self, pitch):
        self.pitch = pitch
        self.freq = convertToFreq(self.pitch)
        
def buildSimonKeyList():
    for i in range(simonKeyCount):
        _tempPosX = LEFT_EDGE + (i * (KEY_WIDTH + GUTTER))
        _tempPosY = height - KEY_HEIGHT - BOTTOM_EDGE
        _tempPos = PVector(_tempPosX, _tempPosY)
        
        _tempCol = colors[i]
        
        # _tempPitch = pitches[i]
        
        simonKeys.append(SimonKey(_tempPos, _tempCol, KEY_WIDTH, KEY_HEIGHT)) # , _tempPitch

def assignPitches():
    for i in range(len(simonKeys)):
        simonKeys[i].assignPitch(pitches[i])

# returns segments of the sequence in round-by-round pieces
def prepareSequence(song, seqLength):
    # tempSeq = song -- doesn't work
    _tempSeq = []
    for i in range(len(song)):
        _tempSeq.append(song[i]) # -- works
        
    _lengthDiff = len(song) - seqLength
    for i in range(_lengthDiff):
        _tempSeq.pop()
        
    return _tempSeq

def updateSimonKeys():
    global isReleased #
    
    # detect and handle mouse interaction
    for i in range(len(simonKeys)):
        if mouseY > height - KEY_HEIGHT - BOTTOM_EDGE and mouseY < height - BOTTOM_EDGE:
            if mouseX > simonKeys[i].pos.x and mouseX < simonKeys[i].pos.x + KEY_WIDTH:
                
                # mouseover
                simonKeys[i].glow()
                
                # mouseclick
                if mousePressed:
                    isReleased = True
                    simonKeys[i].light()
                    
                elif isReleased:
                    simonKeys[i].trigger()
                    
                    # store what the user plays
                    userPlayed.append(i)
                    
                    isReleased = False
            else:
                simonKeys[i].reset()
        else:
            simonKeys[i].reset()
           
def selectSong(prev = -1): # default -1 for first function call 
    global pitches, sequence, songNumber
    
    # randomly select a new song
    songNumber = floor(random(songCount))
    
    # keep trying until you get a different song than last played
    while songNumber == prev:
        songNumber = floor(random(songCount))
        
    if songNumber == 0:
        # sonic (green hill zone) theme by Masato Nakamura
        pitches = ["G4", "A4", "B4", "C5"]
        sequence = [2, 1, 2, 1, 2, 1, 3, 2, 1]
    elif songNumber == 1:        
        # super mario bros entry theme by Koji Kondo
        pitches = ["G3", "C4", "E4", "G4"]
        sequence = [2, 2, 2, 1, 2, 3, 0]
    elif songNumber == 2:
        # darth vader theme by John Williams
        pitches = ["Ab3", "C4", "Eb4", "G4"] # unused 4th note
        sequence = [1, 1, 1, 0, 2, 1, 0, 2, 1]
    elif songNumber == 3:
        # west side story "maria" theme by Leonard Bernstein
        pitches = ["D4", "Ab4", "A4", "B4"]
        sequence = [0, 1, 2, 0, 1, 2, 3, 1, 2, 3, 1, 2]
    # elif songNumber == 4:
        # rocky eye of the tiger theme by Jim Peterik and Frankie Sullivan
        # pitches = ["C3", "D3", "E3", "G3"]
        # sequence = [2, 2, 1, 2, 2, 1, 2, 2, 1, 0]

# used for system playback, gradually returns opacity to default
def resetKeys():
    for simonKey in simonKeys:
        if frameCount % 2 == 0 and simonKey.opa > 128:
            simonKey.opa -= 10
        elif simonKey.opa < 128:
            simonKey.opa = 128

def evaluateUserPlayed():
    global seq, userPlayed, gameState
    
    # prepare a new version of seq 
    _seq = []
    
    # catch user playing too many notes
    if len(userPlayed) > len(seq):
        _diff = len(userPlayed) - len(seq)
        for i in range(_diff):
            userPlayed.pop()
            
    # crop new version so it's the same length of userPlayed
    for i in range(len(userPlayed)):
        _seq.append(seq[i])
        
    # if we're at the last note of the song
    if len(sequence) == len(userPlayed):
        if seq == userPlayed:
            
            # wait a short interval of time and go to win state
            if frameCount % 100 == True:
                gameState = WIN_STATE
                clearUserPlayed()
                
        else:
            gameState = WRONG_STATE
            clearUserPlayed()

    # if we're at the last note of the segment        
    elif len(seq) == len(userPlayed):
        
        # compare the segment to what the user played
        if seq == userPlayed:
            
            # wait a short interval of time and go to listen state
            if frameCount % 100 == True:
                gameState = LISTEN_STATE
                clearUserPlayed()
        else:
            gameState = WRONG_STATE
            clearUserPlayed()
    
    # if it's not the last note of the sequence
    # check to see if it matches so far
    else:
        if _seq != userPlayed:
            gameState = WRONG_STATE
            clearUserPlayed()
            
def clearUserPlayed():
    global userPlayed
    userPlayed = []
    
def resetGame():
    global seqIndex, seqLength, gameOverTimer
    userPlayed = []
    seqIndex = 0
    seqLength = 1
    gameOverTimer = 0

# utility function
def convertToFreq(pitch):
    _tempFreq = 0
    
    if pitch == "C3":
        _tempFreq = 130.81
    elif pitch == "Db3":
        _tempFreq = 138.59
    elif pitch == "D3":
        _tempFreq = 146.83 
    elif pitch == "Eb3":
        _tempFreq = 155.56
    elif pitch == "E3":
        _tempFreq = 164.81
    elif pitch == "F3":
        _tempFreq = 174.61
    elif pitch == "Gb3":
        _tempFreq = 185.00
    elif pitch == "G3":
        _tempFreq = 196.00
    elif pitch == "Ab3":
        _tempFreq = 207.65
    elif pitch == "A3":
        _tempFreq = 220.00
    elif pitch == "Bb3":
        _tempFreq = 233.08
    elif pitch == "B3":
        _tempFreq = 246.94
    elif pitch == "C4":
        _tempFreq = 261.63
    elif pitch == "Db4":
        _tempFreq = 277.18
    elif pitch == "D4":
        _tempFreq = 293.66
    elif pitch == "Eb4":
        _tempFreq = 311.13
    elif pitch == "E4":
        _tempFreq = 329.63
    elif pitch == "F4":
        _tempFreq = 349.23
    elif pitch == "Gb4":
        _tempFreq = 369.99
    elif pitch == "G4":
        _tempFreq = 392.00
    elif pitch == "Ab4":
        _tempFreq = 415.30
    elif pitch == "A4":
        _tempFreq = 440.00
    elif pitch == "Bb4":
        _tempFreq = 466.16
    elif pitch == "B4":
        _tempFreq = 493.88
    elif pitch == "C5":
        _tempFreq = 523.25
    else:
        _tempFreq = 0
        
    return _tempFreq
