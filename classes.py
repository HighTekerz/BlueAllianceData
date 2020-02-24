import numpy as np
import scipy as sp
import time
from scipy import linalg
import requests
import json
colors = ['blue','red']
matchTypeOrder = ['qm','qf','sf','f']
metrics = {2018:{},
           2019:{'adjustPoints':'misc',
                 'autoPoints':'nonContensted',
                 'bay1':'alliance',
                 'bay2':'alliance',
                 'bay3':'alliance',
                 'bay4':'alliance',
                 'bay5':'alliance',
                 'bay6':'alliance',
                 'bay7':'alliance',
                 'bay8':'alliance',
                 'cargoPoints':'alliance',
                 'completeRocketRankingPoint':'rp',
                 'completedRocketFar':'rp',
                 'completedRocketNear':'rp',
                 'endgameRobot1':'team',
                 'endgameRobot2':'team',
                 'endgameRobot3':'team',
                 'foulCount':'foul',
                 'foulPoints':'foul',
                 'habClimbPoints':'nonContested',
                 'habDockingRankingPoint':'rp',
                 'habLineRobot1':'team',
                 'habLineRobot2':'team',
                 'habLineRobot3':'team',
                 'hatchPanelPoints':'alliance',
                 'lowLeftRocketFar':'alliance',
                 'lowLeftRocketNear':'alliance',
                 'lowRightRocketFar':'alliance',
                 'lowRightRocketNear':'alliance',
                 'midLeftRocketFar':'alliance',
                 'midLeftRocketNear':'alliance',
                 'midRightRocketFar':'alliance',
                 'midRightRocketNear':'alliance',
                 'preMatchBay1':'misc',
                 'preMatchBay2':'misc',
                 'preMatchBay3':'misc',
                 'preMatchBay6':'misc',
                 'preMatchBay7':'misc',
                 'preMatchBay8':'misc',
                 'preMatchLevelRobot1':'team',
                 'preMatchLevelRobot2':'team',
                 'preMatchLevelRobot3':'team',
                 'rp':'rp',
                 'sandStormBonusPoints':'nonContested',
                 'techFoulCount':'foul',
                 'teleopPoints':'alliance',
                 'topLeftRocketFar':'alliance',
                 'topLeftRocketNear':'alliance',
                 'topRightRocketFar':'alliance',
                 'topRightRocketNear':'alliance',
                 'totalPoints':'alliance'
                },
           2020:{'initLineRobot1':'team',
                 'initLineRobot2':'team',
                 'initLineRobot3':'team',
                 'endgameRobot1':'team',
                 'endgameRobot2':'team',
                 'endgameRobot3':'team',
                 'autoCellsBottom':'nonContested',
                 'autoCellsOuter':'nonContested',
                 'autoCellsInner':'nonContested',
                 'teleopCellsBottom':'alliance',
                 'teleopCellsOuter':'alliance',
                 'teleopCellsInner':'alliance',
                 'stage1Activated':'misc',
                 'stage2Activated':'misc',
                 'stage3Activated':'misc',
                 'stage3TargetColor':'misc',
                 'endgameRungIsLevel':'nonContested',
                 'autoInitLinePoints':'nonContested',
                 'autoCellPoints':'nonContested',
                 'autoPoints':'nonContested',
                 'teleopPoints':'alliance',
                 'controlPanelPoints':'nonContested',
                 'endgamePoints':'nonContested',
                 'teleopPoints':'alliance',
                 'shieldOperationalRankingPoint':'rp',
                 'shieldEnergizedRankingPoint':'rp',
                 'tba_shieldEnergizedRankingPointFromFoul':'misc',
                 'tba_numRobotsHanging':'misc',
                 'foulCount':'foul',
                 'techFoulCount':'foul',
                 'adjustPoints':'misc', #still don't know what this is
                 'foulPoints':'foul',
                 'rp':'rp',
                 'totalPoints': 'alliance'
                }
          }
tbaTranslation = {2018:{'climbToPoint':{'None':0, 'Levitate':0, 'Parking':5,'Climbing':30, 'Unknown':0},'autoRunToPoints':{'None':0, 'AutoRun':5}},
                  2019:{'endgameRobot':
                        {'None':0,'HabLevel1':3,'HabLevel2':6,'HabLevel3':12},
                        'bay':
                        {'None':0,'Panel':2,'PanelAndCargo':5},
                        'Rocket':
                        {'None':0,'Panel':2,'PanelAndCargo':5},
                        'preMatchBay':
                        {'Cargo':0,'Panel':2},
                        'preMatchLevelRobot':
                        {'None':0,'HabLevel1':3,'HabLevel2':6,'HabLevel3':6},
                        'habLineRobot':
                        {'None':0,'CrossedHabLineInSandstorm':1}},
                  2020:{'endgameRobot':
                        {'Park':5,'Hang':5,'None':0},
                        'endgameRung':
                        {'IsLevel':15,'NotLevel':0},
                        'initLine':
                        {'Excited':5,'None':0},
                        'shield':
                        {'true':1,'false':0},
                        'targetColor':
                        {'lol':10},#idk what to do with this
                        'stage':
                        {'true':1,'false':0}}}
#BIG THING PAY ATTENTION NOAH, at some point we need to actually finalize what we want methods to return
#or should they be void methods
#authorization key needed touse TBA API
auth={'X-TBA-Auth-Key':'WpZWImrGaWBkNJIIbuvmw6CYDDP52XxQf8XrILyI0itHAcZDaGFVn3z72SlRIjF8'}
def removeFRC(teamKey): # converts teram keys like 'frc948' to 948 to make it so stuff sorts properly later
    return int(teamKey[3:])
def removeNewLine(string): #converts JSON of <something> keys API to a python data
    return(json.loads(string[2:len(string)-1].replace('\\n','').replace("\\",'')))
def javaBoolToPy(javaBool):
    if javaBool=='true':
        return True
    return False
def TBAPull(directory): #pulls specific info from tba api and makes it into python usable format
    return(removeNewLine(str(requests.get('http://www.thebluealliance.com/api/v3/'+directory,headers=auth).content)))
class Event:
    global color
    global tbaTranslation
    global metrics
    def __init__(self, year, key):
        if type(year)!=int:
            raise Exception('Years are ints')
        elif year not in range(2019,2021):
            raise Exception('Year not implemented')
        elif type(key)!=str:
            raise Exception('Key must be string')
        #add something to make sure the year key combo is valid
        self.eventKey = str(year)+key
        self.allMetrics = metrics[year]
        self.metricKeys = list(metrics[year].keys())
        self.nonContestedMetrics = [x for x in self.allMetrics if self.allMetrics[x]=='nonContested']
        self.allianceMetrics = [x for x in self.allMetrics if self.allMetrics[x]=='alliance']
        self.teamMetrics = [x for x in self.allMetrics if self.allMetrics[x]=='team']
        self.rpMetrics = [x for x in self.allMetrics if self.allMetrics[x]=='rp']
        self.miscMetrics = [x for x in self.allMetrics if self.allMetrics[x]=='misc']
        self.foulMetrics = [x for x in self.allMetrics if self.allMetrics[x]=='foul']
        self.tbaTranslation = tbaTranslation[year]
        #self.weights = self.weights[year]
        #create a bunch of empty variable so i can test if they are none instead of checking if they exist
        self.teamsList = None
        self.noTeams = None
        self.noQuals = None
        self.quals = None
        self.finals = None
        self.blueMatrix = None
        self.redMatrix = None
        self.rawMetrics = None
        self.RawRed = None
        self.RawBlue = None
        self.nonContestedMatrix = None
        self.contestedMatrix = None
        self.nonContestedInverse = None
        self.contestedInverse = None
        self.noFinals = None
        self.RawBlueF = None
        self.RawRedF = None
        self.rawMetricsF = None
        self.blueMatrixF = None
        self.redMatrixF = None
        self.nonContestedMatrixF = None
        self.contestedMatrixF = None
        self.contestedInverseF = None
        self.nonContestedInverseF = None
        self.opr = None
        self.oprF = None
        self.allMatches = None
    def __repr__(self):
        return('Event '+str(self.eventKey))
    def teams(self):
        if self.noTeams!=None:
            return(None)
        teamsPre = TBAPull('event/'+self.eventKey+'/teams/keys')
        teamsList = [Team(x) for x in teamsPre]
        teamsList.sort()
        self.teamsList = teamsList
        self.noTeams = len(teamsList)
    def matches(self):
        if self.noQuals!=None:
            return(None)
        allMatches = TBAPull('event/'+self.eventKey+'/matches/keys')
        quals = [Match(match) for match in allMatches if 'f' not in match]
        finals = [Match(match) for match in allMatches if 'f' in match]
        quals.sort()
        self.noQuals = len(quals)
        self.noFinals = len(finals)
        self.quals = quals
        self.finals = finals
        allMatches = quals+finals
        allMatches.sort()
        self.allMatches = allMatches
    def participation(self): #creates incidence matrix for teams and events
        if type(self.blueMatrix)!=type(None):
            return(None)
        #todo, determine whether any teams were absent
        self.matches()
        self.teams()
        blueParticipation = np.zeros((self.noQuals,self.noTeams))
        redParticipation = np.zeros((self.noQuals,self.noTeams))
        blueParticipationF = np.zeros((self.noFinals+self.noQuals,self.noTeams))
        redParticipationF = np.zeros((self.noFinals+self.noQuals,self.noTeams))
        for match in self.quals:
            match.score()
            for team in match.blue:
                blueParticipation[int(match.matchNo)-1][(self.teamsList).index(team)] = 1
            for team in match.red:
                redParticipation[int(match.matchNo)-1][(self.teamsList).index(team)] = 1
        self.blueMatrix = blueParticipation
        self.redMatrix = redParticipation
        self.nonContestedMatrix = np.concatenate((blueParticipation,redParticipation))
        self.contestedMatrix = np.concatenate((self.nonContestedMatrix,
                                               np.concatenate((-redParticipation,-blueParticipation))),
                                              axis=1)
        for match in self.allMatches:
            match.score()
            for team in match.blue:
                blueParticipationF[(self.allMatches).index(match)][(self.teamsList).index(team)] = 1
            for team in match.red:
                redParticipationF[(self.allMatches).index(match)][(self.teamsList).index(team)] = 1
        self.blueMatrixF = blueParticipationF
        self.redMatrixF = redParticipationF
        self.nonContestedMatrixF = np.concatenate((blueParticipationF,redParticipationF))
        self.contestedMatrixF = np.concatenate((self.nonContestedMatrixF,
                                               np.concatenate((-redParticipationF,-blueParticipationF))),
                                              axis=1)
        return(self.blueMatrix,self.redMatrix)
    def inverse(self, includeFinals=False):
        if type(self.nonContestedInverse)!=type(None):
            return(None)
        self.participation()
        self.contestedInverse = np.linalg.pinv(self.contestedMatrix)
        self.nonContestedInverse = np.linalg.pinv(self.nonContestedMatrix)
        self.contestedInverseF = np.linalg.pinv(self.contestedMatrixF)
        self.nonContestedInverseF = np.linalg.pinv(self.nonContestedMatrixF)
        return(self.contestedInverse,self.nonContestedInverse)
    def raw(self): #creates array of arrays containing raw metric values for all matches
        if self.rawMetrics!=None:
            return(None)
        self.matches()
        self.teams()
        #can't use np array for this since that only supports numerical types as entries :(
        RawBlue = []
        RawRed = []
        for match in self.quals:
            match.score()
            RawBlue.append(list(match.rawBlue.values()))
            RawRed.append(list(match.rawRed.values()))
        self.RawBlue = RawBlue
        self.RawRed = RawRed
        self.rawMetrics = RawBlue+RawRed
        RawBlueF = []
        RawRedF = []
        for match in self.allMatches:
            match.score()
            RawBlueF.append(list(match.rawBlue.values()))
            RawRedF.append(list(match.rawRed.values()))
        self.RawBlueF = RawBlueF
        self.RawRedF = RawRedF
        self.rawMetricsF = RawBlueF+RawRedF
    #don't like this name, night change before final
    def processing(self, metric, includeFinals=False):
        if metric not in self.metricKeys:
            raise Exception('Not a valid metric for this year, check TBA for metrics')
        metricIndex = self.metricKeys.index(metric)
        metricType = self.allMetrics[metric]
        self.raw()
        for reg in self.tbaTranslation:
            if reg in metric:
                points = lambda x: reg[x]
                break
        else:
            points = lambda x: int(javaBoolToPy(x))
        if includeFinals:
            includedMatches = self.rawMetricsF
        else:
            includedMatches = self.rawMetrics
        metricValues = [includedMatches[x][self.metricKeys.index(metric)] for x in range(self.noTeams)]
        if metricType=='team':
            pass
        elif metricType=='alliance':
            inverse = self.inverse()[0]
            return(inverse@np.array(metricValues))
    def getOPR(self):
        if type(self.opr)!=type(None):
            return(None)
        self.raw()
        self.inverse()
        scoreValues = [self.rawMetrics[x][self.metricKeys.index('totalPoints')] for x in range(2*self.noQuals)]
        self.opr = self.nonContestedInverse@scoreValues
        scoreValuesF = [self.rawMetricsF[x][self.metricKeys.index('totalPoints')] for x in range(2*self.noQuals+2*self.noFinals)]
        self.oprF = self.nonContestedInverseF@scoreValuesF
        
class Match:
    global matchTypeOrder
    def __init__(self, matchKey):
        self.matchKey = matchKey
        split = matchKey.split('_')
        #rename temp
        temp = split[1]
        self.eventKey = split[0]
        #the handling of these case feels really awful, maybe learn regex
        #come up with a better way of assigning match numbers to finals matches
        if 'sf' in temp:
            self.matchType = 'sf'
            self.matchNo = temp[2:]
        elif 'qf' in temp:
            self.matchType = 'qf'
            self.matchNo = temp[2:]
            
        elif 'f' in temp:
            self.matchType = 'f'
            self.matchNo = temp[1:]
        else:
            self.matchType = 'qm'
            self.matchNo = temp[2:]
        self.blue = None
        self.red = None
        self.blueScore =None
        self.redScore = None
        self.winner = None
        self.happened = None
        self.rawBlue = None
        self.rawRed = None
        self.time = None
    def __repr__(self):
        return('Match '+str(self.matchKey))
    def score(self):
        if self.blue!=None:
            return(None)
        matchData = TBAPull('match/'+self.matchKey)
        self.blue = [Team(x) for x in matchData["alliances"]['blue']['team_keys']]
        self.red = [Team(x) for x in matchData["alliances"]['red']['team_keys']]
        self.blueScore = matchData['score_breakdown']['blue']
        self.redScore = matchData['score_breakdown']['red']
        self.winner = matchData['winning_alliance']
        self.rawRed = matchData['score_breakdown']['red']
        self.rawBlue = matchData['score_breakdown']['blue']
        self.time = matchData['actual_time']
        if self.time==None:
            self.happened = False
        else:
            self.happened = True
        return(self.blue,self.red,self.blueScore,self.redScore,self.winner,self.happened)
    #following two things allow me to easily sort matches
    def __eq__(self, second):
        if self.eventKey == second.eventKey:
            if self.matchKey == second.matchKey:
                return True
            else:
                return False
        else:
            raise Exception('Must be from same event')
    def __lt__(self, second):
        if self.eventKey == second.eventKey:
            if matchTypeOrder.index(self.matchType)!=matchTypeOrder.index(second.matchType):
                return(matchTypeOrder.index(self.matchType)<matchTypeOrder.index(second.matchType))
            elif self.matchType=='qm':
                return(int(self.matchNo)<int(second.matchNo))
            elif self.matchNo[1]!=second.matchNo[1]:
                return(self.matchNo[1]<second.matchNo[1])
            else:
                return(self.matchNo[-1]<second.matchNo[-1])
        else:
            raise Exception('Must be from same event')
class Team: #more functionality will be added eventually but I'm not sure what
    def __init__(self, number):
        if str(number)[:3]=='frc':
            self.number = removeFRC(number)
        else:
            self.number = number
    def __eq__(self, second):
        return(self.number==second.number)
    def __lt__(self, second):
        return(self.number<second.number)
    def events(self, year): #generates dict of event key name pairs for a given year
        if eventList!=None:
            return(eventList)
        eventList = TBAPull('team/frc'+str(self.number)+'/events/'+str(year)+'/simple')
        self.eventList = dict([(event['key'],event['name']) for event in eventList])
        return(eventList)
    def __repr__(self):
        return('Team '+str(self.number))
    def __int__(self):
        return(self.number)
