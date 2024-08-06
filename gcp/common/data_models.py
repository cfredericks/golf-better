"""
Application data models
"""

class Champion:
    def __init__(self, displayName, playerId):
        self.displayName = displayName
        self.playerId = playerId

    def __repr__(self):
        return f"Champion(displayName='{self.displayName}', playerId='{self.playerId}')"

    def __str__(self):
        return self.__repr__()

class TournamentCategoryInfo:
    def __init__(self, type, logoLight, logoDark, label):
        self.type = type
        self.logoLight = logoLight
        self.logoDark = logoDark
        self.label = label

    def __repr__(self):
        return f"TournamentCategoryInfo(type='{self.type}', logoLight='{self.logoLight}', logoDark='{self.logoDark}', label='{self.label}')"

    def __str__(self):
        return self.__repr__()

class Tournament:
    def __init__(self, tournamentName, id, beautyImage, champion, champions, championEarnings, championId, city, country,
                 countryCode, courseName, date, dateAccessibilityText, purse, sortDate, startDate, state, stateCode, status,
                 tournamentStatus, ticketsURL, tourStandingHeading, tourStandingValue, tournamentLogo, display,
                 sequenceNumber, tournamentCategoryInfo):
        self.tournamentName = tournamentName
        self.id = id
        self.beautyImage = beautyImage
        self.champion = champion
        self.champions = champions
        self.championEarnings = championEarnings
        self.championId = championId
        self.city = city
        self.country = country
        self.countryCode = countryCode
        self.courseName = courseName
        self.date = date
        self.dateAccessibilityText = dateAccessibilityText
        self.purse = purse
        self.sortDate = sortDate
        self.startDate = startDate
        self.state = state
        self.stateCode = stateCode
        self.status = status
        self.tournamentStatus = tournamentStatus
        self.ticketsURL = ticketsURL
        self.tourStandingHeading = tourStandingHeading
        self.tourStandingValue = tourStandingValue
        self.tournamentLogo = tournamentLogo
        self.display = display
        self.sequenceNumber = sequenceNumber
        self.tournamentCategoryInfo = tournamentCategoryInfo

    def __repr__(self):
        return (f"PGATournament(tournamentName='{self.tournamentName}', id='{self.id}', beautyImage='{self.beautyImage}', champion='{self.champion}', "
                f"champions={self.champions}, championEarnings='{self.championEarnings}', championId='{self.championId}', city='{self.city}', "
                f"country='{self.country}', countryCode='{self.countryCode}', courseName='{self.courseName}', date='{self.date}', "
                f"dateAccessibilityText='{self.dateAccessibilityText}', purse='{self.purse}', sortDate='{self.sortDate}', startDate='{self.startDate}', "
                f"state='{self.state}', stateCode='{self.stateCode}', status='{self.status}', tournamentStatus='{self.tournamentStatus}', "
                f"ticketsURL='{self.ticketsURL}', tourStandingHeading='{self.tourStandingHeading}', tourStandingValue='{self.tourStandingValue}', "
                f"tournamentLogo='{self.tournamentLogo}', display='{self.display}', sequenceNumber='{self.sequenceNumber}', "
                f"tournamentCategoryInfo={self.tournamentCategoryInfo})")

    def __str__(self):
        return self.__repr__()

class PlayerBio:
    def __init__(self, id, age, education, turnedPro):
        self.id = id
        self.age = age
        self.education = education
        self.turnedPro = turnedPro

    def __repr__(self):
        return f"PlayerBio(id='{self.id}', age={self.age}, education='{self.education}', turnedPro={self.turnedPro})"

    def __str__(self):
        return self.__repr__()

class Player:
    def __init__(self, id, isActive, firstName, lastName, shortName, displayName, amateur, tourBound, alphaSort, country, countryFlag, headshot, lineColor, bettingProfile, abbreviations, abbreviationsAccessibilityText, playerBio):
        self.id = id
        self.isActive = isActive
        self.firstName = firstName
        self.lastName = lastName
        self.shortName = shortName
        self.displayName = displayName
        self.amateur = amateur
        self.tourBound = tourBound
        self.alphaSort = alphaSort
        self.country = country
        self.countryFlag = countryFlag
        self.headshot = headshot
        self.lineColor = lineColor
        self.bettingProfile = bettingProfile
        self.abbreviations = abbreviations
        self.abbreviationsAccessibilityText = abbreviationsAccessibilityText
        self.playerBio = playerBio

    def __repr__(self):
        return (f"Player(id={self.id}, isActive={self.isActive}, firstName={self.firstName}, lastName={self.lastName}, "
                f"shortName={self.shortName}, displayName={self.displayName}, amateur={self.amateur}, tourBound={self.tourBound}, "
                f"alphaSort={self.alphaSort}, country={self.country}, countryFlag={self.countryFlag}, headshot={self.headshot}, "
                f"lineColor={self.lineColor}, bettingProfile={self.bettingProfile}, abbreviations={self.abbreviations}, "
                f"abbreviationsAccessibilityText={self.abbreviationsAccessibilityText}, playerBio={self.playerBio})")

    def __str__(self):
        return self.__repr__()

class PlayerRowV3:
    def __init__(self, id, leaderboardSortOrder, player, scoringData):
        self.id = id
        self.leaderboardSortOrder = leaderboardSortOrder
        self.player = player
        self.scoringData = scoringData

    def __repr__(self):
        return (f"PlayerRowV3(id='{self.id}', leaderboardSortOrder={self.leaderboardSortOrder}, player={self.player}, "
                f"scoringData={self.scoringData})")

    def __str__(self):
        return self.__repr__()

class ScoringData:
    def __init__(self, position, total, totalSort, thru, thruSort, score, scoreSort, courseId, groupNumber, currentRound, oddsToWin, oddsSwing, oddsOptionId, oddsSort, backNine, roundHeader, rounds, movementDirection, movementAmount, playerState, rankingMovement, rankingMovementAmount, rankingMovementAmountSort, totalStrokes, official, officialSort, projected, projectedSort, hasStoryContent, storyContentRounds, roundStatus, rankLogoLight, rankLogoDark):
        self.position = position
        self.total = total
        self.totalSort = totalSort
        self.thru = thru
        self.thruSort = thruSort
        self.score = score
        self.scoreSort = scoreSort
        self.courseId = courseId
        self.groupNumber = groupNumber
        self.currentRound = currentRound
        self.oddsToWin = oddsToWin
        self.oddsSwing = oddsSwing
        self.oddsOptionId = oddsOptionId
        self.oddsSort = oddsSort
        self.backNine = backNine
        self.roundHeader = roundHeader
        self.rounds = rounds
        self.movementDirection = movementDirection
        self.movementAmount = movementAmount
        self.playerState = playerState
        self.rankingMovement = rankingMovement
        self.rankingMovementAmount = rankingMovementAmount
        self.rankingMovementAmountSort = rankingMovementAmountSort
        self.totalStrokes = totalStrokes
        self.official = official
        self.officialSort = officialSort
        self.projected = projected
        self.projectedSort = projectedSort
        self.hasStoryContent = hasStoryContent
        self.storyContentRounds = storyContentRounds
        self.roundStatus = roundStatus
        self.rankLogoLight = rankLogoLight
        self.rankLogoDark = rankLogoDark

    def __repr__(self):
        return (f"ScoringData(position='{self.position}', total='{self.total}', totalSort={self.totalSort}, thru='{self.thru}', thruSort={self.thruSort}, "
                f"score='{self.score}', scoreSort={self.scoreSort}, courseId='{self.courseId}', groupNumber={self.groupNumber}, currentRound={self.currentRound}, "
                f"oddsToWin='{self.oddsToWin}', oddsSwing='{self.oddsSwing}', oddsOptionId='{self.oddsOptionId}', oddsSort={self.oddsSort}, backNine={self.backNine}, "
                f"roundHeader='{self.roundHeader}', rounds={self.rounds}, movementDirection='{self.movementDirection}', movementAmount='{self.movementAmount}', "
                f"playerState='{self.playerState}', rankingMovement='{self.rankingMovement}', rankingMovementAmount='{self.rankingMovementAmount}', "
                f"rankingMovementAmountSort={self.rankingMovementAmountSort}, totalStrokes='{self.totalStrokes}', official='{self.official}', officialSort={self.officialSort}, "
                f"projected='{self.projected}', projectedSort={self.projectedSort}, hasStoryContent={self.hasStoryContent}, storyContentRounds={self.storyContentRounds}, "
                f"roundStatus='{self.roundStatus}', rankLogoLight='{self.rankLogoLight}', rankLogoDark='{self.rankLogoDark}')")

    def __str__(self):
        return self.__repr__()

class Hole:
    def __init__(self, holeNumber, par, score, sequenceNumber, status, yardage, roundScore):
        self.holeNumber = holeNumber
        self.par = par
        self.score = score
        self.sequenceNumber = sequenceNumber
        self.status = status
        self.yardage = yardage
        self.roundScore = roundScore

    def __repr__(self):
        return (f"Hole(holeNumber={self.holeNumber}, par={self.par}, score='{self.score}', sequenceNumber={self.sequenceNumber}, status='{self.status}', "
                f"yardage={self.yardage}, roundScore='{self.roundScore}')")

    def __str__(self):
        return self.__repr__()

class NineHoles:
    def __init__(self, holes, totalLabel, parTotal, total):
        self.holes = holes
        self.totalLabel = totalLabel
        self.parTotal = parTotal
        self.total = total

    def __repr__(self):
        return (f"NineHoles(holes={self.holes}, totalLabel='{self.totalLabel}', parTotal={self.parTotal}, total='{self.total}')")

    def __str__(self):
        return self.__repr__()

class RoundScore:
    def __init__(self, complete, currentHole, currentRound, firstNine, secondNine, roundNumber, groupNumber, courseName, courseId, parTotal, total, scoreToPar):
        self.complete = complete
        self.currentHole = currentHole
        self.currentRound = currentRound
        self.firstNine = firstNine
        self.secondNine = secondNine
        self.roundNumber = roundNumber
        self.groupNumber = groupNumber
        self.courseName = courseName
        self.courseId = courseId
        self.parTotal = parTotal
        self.total = total
        self.scoreToPar = scoreToPar

    def __repr__(self):
        return (f"RoundScore(complete={self.complete}, currentHole={self.currentHole}, currentRound={self.currentRound}, "
                f"firstNine={self.firstNine}, secondNine={self.secondNine}, roundNumber={self.roundNumber}, groupNumber={self.groupNumber}, courseName='{self.courseName}', "
                f"courseId='{self.courseId}', parTotal={self.parTotal}, total='{self.total}', scoreToPar='{self.scoreToPar}')")

    def __str__(self):
        return self.__repr__()

class ScorecardV3:
    def __init__(self, tournamentName, id, currentRound, backNine, groupNumber, player, roundScores, currentHole, playerState, hideSov, profileEnabled):
        self.tournamentName = tournamentName
        self.id = id
        self.currentRound = currentRound
        self.backNine = backNine
        self.groupNumber = groupNumber
        self.player = player
        self.roundScores = roundScores
        self.currentHole = currentHole
        self.playerState = playerState
        self.hideSov = hideSov
        self.profileEnabled = profileEnabled

    def __repr__(self):
        return (f"ScorecardV3(tournamentName={self.tournamentName!r}, id={self.id!r}, "
                f"currentRound={self.currentRound!r}, backNine={self.backNine!r}, groupNumber={self.groupNumber!r}, "
                f"player={self.player!r}, roundScores={self.roundScores!r}, currentHole={self.currentHole!r}, "
                f"playerState={self.playerState!r}, hideSov={self.hideSov!r}, profileEnabled={self.profileEnabled!r})")

    def __str__(self):
        return self.__repr__()

class PGATournament:
    def __init__(self, id, name, start_date, is_completed, data, last_updated):
        self.id = id
        self.name = name
        self.start_date = start_date
        self.is_completed = is_completed
        self.data = data
        self.last_updated = last_updated

    def __repr__(self):
        return (f"PGATournament(id='{self.id}', name='{self.name}', start_date='{self.start_date}', "
                f"is_completed={self.is_completed}, data={self.data}, last_updated='{self.last_updated}')")

    def __str__(self):
        return self.__repr__()

class PGAPlayer:
    def __init__(self, id, name, data, last_updated):
        self.id = id
        self.name = name
        self.data = data
        self.last_updated = last_updated

    def __repr__(self):
        return (f"PGAPlayer(id='{self.id}', name='{self.name}', data={self.data}, "
                f"last_updated='{self.last_updated}')")

    def __str__(self):
        return self.__repr__()

class PGALeaderboardPlayer:
    def __init__(self, id, tournament_id, player_id, data, last_updated):
        self.id = id
        self.tournament_id = tournament_id
        self.player_id = player_id
        self.data = data
        self.last_updated = last_updated

    def __repr__(self):
        return (f"PGALeaderboardPlayer(id='{self.id}', tournament_id='{self.tournament_id}', player_id='{self.player_id}', "
                f"data={self.data}, last_updated='{self.last_updated}')")

    def __str__(self):
        return self.__repr__()

class PGAPlayerScorecard:
    def __init__(self, id, tournament_id, player_id, data, last_updated):
        self.id = id
        self.tournament_id = tournament_id
        self.player_id = player_id
        self.data = data
        self.last_updated = last_updated

    def __repr__(self):
        return (f"PGAPlayerScorecard(id='{self.id}', tournament_id='{self.tournament_id}', player_id='{self.player_id}', "
                f"data={self.data}, last_updated='{self.last_updated}')")

    def __str__(self):
        return self.__repr__()

class User:
    def __init__(self, id, name, email, created, last_updated, last_login):
        self.id = id
        self.name = name
        self.email = email
        self.created = created
        self.last_updated = last_updated
        self.last_login = last_login

    def __repr__(self):
        return (f"User(id='{self.id}', name='{self.name}', email='{self.email}', "
                f"created='{self.created}', last_updated='{self.last_updated}', last_login='{self.last_login}')")

    def __str__(self):
        return self.__repr__()