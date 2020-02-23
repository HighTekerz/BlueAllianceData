import numpy as np
import scipy as sp
import time
from scipy import linalg
import requests
import json
#BIG THING PAY ATTENTION NOAH, at some point we need to actually finalize what we want methods to return
#or should they be void methods
#authorization key needed touse TBA API
auth={'X-TBA-Auth-Key':'WpZWImrGaWBkNJIIbuvmw6CYDDP52XxQf8XrILyI0itHAcZDaGFVn3z72SlRIjF8'}
def removeFRC(teamKey): # converts teram keys like 'frc948' to 948 to make it so stuff sorts properly later
    return int(teamKey[3:])
def removeNewLine(string): #converts JSON of <something> keys API to a python data
    return(json.loads(string[2:len(string)-1].replace('\\n','').replace("\\",'')))
def TBAPull(directory): #pulls specific info from tba api and makes it into python usable format
    return(removeNewLine(str(requests.get('http://www.thebluealliance.com/api/v3/'+directory,headers=auth).content)))
class Event:
    colors = ['blue','red']
    #fill these in for all years later
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
    #converts data typed as a string from TBA to the point value it represents
    #can't fill out until I know what the possible responses for 2020 are
    #need to decide an efficent way to encode which things in this correspond to which metrics
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
    def __init__(self, year, key):
        if type(year)!=int:
            raise Exception('Years are ints')
        elif year not in range(2019,2021):
            raise Exception('Year not implemented')
        elif type(key)!=str:
            raise Exception('Key must be string')
        #add something to make sure the year key combo is valid
        self.eventKey = str(year)+key
        self.allMetrics = self.metrics[year]
        self.metricKeys = list(self.metrics[year].keys())
        self.nonContestedMetrics = [x for x in self.allMetrics if self.allMetrics[x]=='nonContested']
        self.allianceMetrics = [x for x in self.allMetrics if self.allMetrics[x]=='alliance']
        self.teamMetrics = [x for x in self.allMetrics if self.allMetrics[x]=='team']
        self.rpMetrics = [x for x in self.allMetrics if self.allMetrics[x]=='rp']
        self.miscMetrics = [x for x in self.allMetrics if self.allMetrics[x]=='misc']
        self.foulMetrics = [x for x in self.allMetrics if self.allMetrics[x]=='foul']
        self.tbaTranslation = self.tbaTranslation[year]
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
    def teams(self):
        if self.noTeams!=None:
            return(self.teamsList,self.noTeams)
        teamsPre = TBAPull('event/'+self.eventKey+'/teams/keys')
        teamsList = [Team(x) for x in teamsPre]
        teamsList.sort()
        self.teamsList = teamsList
        self.noTeams = len(teamsList)
        return(self.teamsList,self.noTeams)
    def matches(self):
        if self.noQuals!=None:
            return(self.quals,self.finals,self.noQuals)
        allMatches = TBAPull('event/'+self.eventKey+'/matches/keys')
        quals = [Match(match) for match in allMatches if 'f' not in match]
        finals = [Match(match) for match in allMatches if 'f' in match]
        quals.sort()
        self.noQuals = len(quals)
        self.quals = quals
        self.finals = finals
        return(self.quals,self.finals,self.noQuals)
    def participation(self): #creates incidence matrix for teams and events
        if type(self.blueMatrix)!=type(None):
            return(self.blueMatrix,self.redMatrix)
        #todo, determine whether any teams were absent
        self.matches()
        self.teams()
        blueParticipation = np.zeros((self.noQuals,self.noTeams))
        redParticipation = np.zeros((self.noQuals,self.noTeams))
        for match in self.quals:
            match.score()
            for team in match.blue:
                blueParticipation[int(match.matchNo)-1][(self.teamsList).index(team)] = 1
        for match in self.quals:
            for team in match.red:
                redParticipation[int(match.matchNo)-1][(self.teamsList).index(team)] = 1
        self.blueMatrix = blueParticipation
        self.redMatrix = redParticipation
        self.nonContestedMatrix = np.concatenate((blueParticipation,redParticipation))
        self.contestedMatrix = np.concatenate((self.nonContestedMatrix,
                                               np.concatenate((-redParticipation,-blueParticipation))),
                                              axis=1)
        return(self.blueMatrix,self.redMatrix)
    def inverse(self):
        if type(self.nonContestedInverse)!=type(None):
            return(self.contestedInverse,self.nonContestedInverse)
        self.participation()
        self.contestedInverse = np.linalg.pinv(self.contestedMatrix)
        self.nonContestedInverse = np.linalg.pinv(self.nonContestedMatrix)
        return(self.contestedInverse,self.nonContestedInverse)
    def raw(self): #creates array of arrays containing raw metric values for all matches
        if self.rawMetrics!=None:
            return(self.rawMetrics)
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
        return(self.RawBlue,self.RawRed)
    #don't like this name, night change before final
    def processing(self, metric):
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
            points = lambda x: int(x)
        metricValues = []
        for match in self.rawMetrics:
            metricValues.append(points(match[metricIndex]))
        if metricType=='team':
            pass
        elif metricType=='alliance':
            inverse = self.inverse()[0]
            return(inverse@np.array(metricValues))
    def opr(self):
        self.raw()
        metricValues = []
        for match in self.rawMetrics:
            metricValues.append(match[self.metricKeys.index('totalPoints')])
        inverse = self.inverse()[1]
        return(inverse@np.array(metricValues))
class Match:
    def __init__(self, matchKey):
        self.matchKey = matchKey
        split = matchKey.split('_')
        #rename temp
        temp = split[1]
        self.eventKey = split[0]
        #the handling of these case feels really awful, maybe learn regex
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
    def score(self):
        if self.blue!=None:
            return(self.blue,self.red,self.blueScore,self.redScore,self.winner,self.happened)
        matchData = TBAPull('match/'+self.matchKey)
        #change red and blue to return team objects at some point without breaking stuff
        self.blue = [Team(x) for x in matchData["alliances"]['blue']['team_keys']]
        self.red = [Team(x) for x in matchData["alliances"]['blue']['team_keys']]
        self.blueScore = matchData['score_breakdown']['blue']
        self.redScore = matchData['score_breakdown']['red']
        self.winner = matchData['winning_alliance']
        self.rawRed = matchData['score_breakdown']['red']
        self.rawBlue = matchData['score_breakdown']['blue']
        if matchData['actual_time']==None:
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
            if self.matchType == second.matchType == 'qm':
                return(int(self.matchNo)<int(second.matchNo))
            else:
                raise Exception('Comparison between match types other than qualifiers not implemented')
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
