import sys
import os


grid = []
validdigs = []
remcoldigs = []
remrowdigs = []
remunitdigs = []

allrules = "ourcs"


def printhelp():
    print("Usage: ", sys.argv[0], " <file|grid>")
    print("A  grid is 81 digits, 0 is used for empty cells")
    print("A file consists of lines of grids")
    print("")
    print("--output <file>       Outputs to file")
    print("--steps               Output steps along with solution")
    print("--start               Output starting grid along with solution")
    print("--format              Print sudoku boards in a human-readable format")
    print("--allow <rulestr>     Only allow these rules to be used")
    print("--disallow <rulestr>  Don't allow these rules to be used")
    print("--rules               Print the rules used in --steps")
    print("-h --help             Print this message")

    return 0

def printrules():
    print("Rules are of form rule(args)")
    print("Gives what value is placed in what index (0-indexed), ")
    print("and additional information about the rule used")
    print("")
    print("o(x,y)       Only possible digit at x is y")
    print("u(x,y)       Only possible place for y in x's unit")
    print("r(x,y)       Only possible place for y in x's row")
    print("c(x,y)       Only possible place for y in x's column")
    # For example cells [2, 3], [2, 3] means no other 2 or 3 in group,
    # and cells [2, 3], [2, 3, 4] with no 2 or 3 elsewhere means 4 can be removed
    # This also extends to just where n cells have non-zero subset of the same n digits, 
    # for example [2, 3], [3, 4], [2, 4] means no other 2, 3, or 4 in group
    print("p(x1,...,xn) These cells all have the same n possible digits")
    # For example a block with [2, 3], [1, 2, 4] on same row, means no other 2 in the row,
    # assuming the block has no other cell with 2
    print("l(x1,x2,x3?) These cells in same block have a digit which blocks a row or column")
    # Four cells parallel both ways have a same possible digit that doesn't appear elsewhere
    # on the rows or columns, so other digits from the columns / rows can then be removed
    print("x(x1,...,x4) \"X-wing\" technique")
    # One cell with only [x, y], and two cells in the same block, row, or column with only [x, z] and [y, z]
    # (z should be the same), then at all "intersections" (can be multiple in same block as one of the two) of those two cells, z can be removed
    print("y(x1,x2,x3)  \"Y-wing\" technique")
    # Like a 3x3 X-wing, nine cells parallel both ways have a same possible digits that doesn't appear
    # elsewhere on the rows or columns, so other digits from the columns / rows can then be removed
    print("z(x1,...,x9) \"Swordfish\" technique")
    # Two cells with y are on same row / column (which may have other y), two cells are on the same column / row
    # as cell 1 and 2 respectively, and are not on the same row / column as each other
    # There are also no other y in the column / row of cell 3 and 4 (other than cell 1 or 2)
    # Then any cells that intersect both 3 and 4 cannot have y
    #print("k(x1,...,x4) \"Skyscraper\" technique")
    # Like a skyscraper but cell 1 and 2 are in the same block, and 3 and 4 are oriented orthogonally from that block
    # Their intersection (one cell) then cannot have y
    #print("2(x1,...,x4) \"2-String kite technique")

    # Maybe combine skyscraper, 2-string kite, and crane as an AIC rule?
    # Two strong links (one is false means other is true) connected by a weak link (one is true means other is false)
    # means that any cell that see both strong link endpoints cannot have y

    #print("b(x1,y,...,xn) x1 sees both parities of strongly-linked chain of xi, cannot have y")

    print("s(x,y)       Basic recursive search, used when all other rules fail")

def setgrid(gridstr: str):
    global grid

    grid = [gridstr[i] for i in range(len(gridstr))]

def validategrid(printerr: bool = True):
    global grid

    if len(grid) != 81:
        if printerr:
            print("Invalid grid: ", grid, "\nGrids must be 81 characters long")
        return False
    for i in range(len(grid)):
        if not grid[i].isdigit():
            if printerr:
                print("Invalid grid: ", grid, "\nGrids must contain only digits")
            return False

    return True

def getgridstr(grid, formatted = False):
    s = ""
    if not formatted:
        for i in range(len(grid)):
            s = s + grid[i]
    
    else:
        for i in range(len(grid)):
            if i%3 == 0 and i%9 != 0:
                s = s + "|"
            if i%27 == 0 and i != 0:
                s = s + "---------+---------+---------\n"
            s = s + f" {grid[i]} "
            if i%9 == 8:
                s = s + "\n"
    
    return s

def gridsolved():
    return not ("0" in grid)

def getcellrow(cell: int):
    return cell//9

def getcellcol(cell: int):
    return cell%9

def getcellunit(cell: int):
    return ((cell%9)//3) + 3*((cell//9)//3)

def getrowcells(row: int):
    return [row*9 + c for c in range(9)]

def getcolcells(col: int):
    return [9*r + col for r in range(9)]

def getunitcells(unit: int):
    r = 3*(unit//3)
    c = 3*(unit%3)
    return [9*(r) + (c) + 9*(i//3) + (i%3) for i in range(9)]

def countcellspossibledigcounts(cells):
    global validdigs

    res = {"1" : 0, "2" : 0, "3" : 0, "4" : 0, "5" : 0,"6" : 0, "7" : 0,"8" : 0, "9" : 0}

    for i in cells:
        for c in validdigs[i]:
            res[c] += 1

    return res

def findpossibledigincells(cells, dig: str):
    global validdigs

    for i in cells:
        if dig in validdigs[i]:
            return i

    return -1

# Resets validdigs, remcoldigs, remrowdigs, and remunitdigs
def resetgridparams():
    global grid
    global validdigs
    global remcoldigs
    global remrowdigs
    global remunitdigs
    
    validdigs = ["123456789" for i in range(81)]
    remcoldigs = ["123456789" for i in range(9)]
    remrowdigs = ["123456789" for i in range(9)]
    remunitdigs = ["123456789" for i in range(9)]

    for i in range(81):
        c = grid[i]
        if c != "0":
            validdigs[i] = c

            col = getcellcol(i)
            row = getcellrow(i)
            unit = getcellunit(i)

            remcoldigs[col] = remcoldigs[col].replace(c, "")
            for celli in getcolcells(col):
                if i == celli:
                    continue
                validdigs[celli] = validdigs[celli].replace(c, "")

            remrowdigs[row] = remrowdigs[row].replace(c, "")
            for celli in getrowcells(row):
                if i == celli:
                    continue
                validdigs[celli] = validdigs[celli].replace(c, "")

            remunitdigs[unit] = remunitdigs[unit].replace(c, "")
            for celli in getunitcells(unit):
                if i == celli:
                    continue
                validdigs[celli] = validdigs[celli].replace(c, "")

def updategridparams(i: int):
    global grid
    global validdigs
    global remcoldigs
    global remrowdigs
    global remunitdigs

    c = grid[i]
    if c != "0":
        validdigs[i] = c

        col = getcellcol(i)
        row = getcellrow(i)
        unit = getcellunit(i)

        remcoldigs[col] = remcoldigs[col].replace(c, "")
        for celli in getcolcells(col):
            if i == celli:
                continue
            validdigs[celli] = validdigs[celli].replace(c, "")

        remrowdigs[row] = remrowdigs[row].replace(c, "")
        for celli in getrowcells(row):
            if i == celli:
                continue
            validdigs[celli] = validdigs[celli].replace(c, "")

        remunitdigs[unit] = remunitdigs[unit].replace(c, "")
        for celli in getunitcells(unit):
            if i == celli:
                continue
            validdigs[celli] = validdigs[celli].replace(c, "")


def applyrules(rules: str = "*"):
    global grid
    global validdigs
    global remcoldigs
    global remrowdigs
    global remunitdigs

    # BASIC RULE
    if rules == "*" or "o" in rules:
        for i in range(81):
            if grid[i] == "0" and len(validdigs[i]) == 1:

                return (True, f"o({i},{validdigs[i]})", i, validdigs[i])

    if rules == "*" or "r" in rules:
        # CHECK IF ROW HAS ONLY ONE POSSIBLE PLACE FOR y
        for r in range(9):
            possiblecounts = countcellspossibledigcounts(getrowcells(r))

            for rowdig in remrowdigs[r]:
                if possiblecounts[rowdig] == 1:
                    celli = findpossibledigincells(getrowcells(r), rowdig)

                    return (True, f"r({celli},{rowdig})", celli, rowdig)

    if rules == "*" or "c" in rules:
        # CHECK IF COL HAS ONLY ONE POSSIBLE PLACE FOR y
        for c in range(9):
            possiblecounts = countcellspossibledigcounts(getcolcells(c))

            for coldig in remcoldigs[c]:
                if possiblecounts[coldig] == 1:
                    celli = findpossibledigincells(getcolcells(c), coldig)

                    return (True, f"c({celli},{coldig})", celli, coldig)
            
    if rules == "*" or "u" in rules:
        # CHECK IF UNIT HAS ONLY ONE POSSIBLE PLACE FOR y
        for u in range(9):
            possiblecounts = countcellspossibledigcounts(getunitcells(u))

            for unitdig in remunitdigs[u]:
                if possiblecounts[unitdig] == 1:
                    celli = findpossibledigincells(getunitcells(u), unitdig)

                    return (True, f"u({celli},{unitdig})", celli, unitdig)

    

    #Returns (success, step, celli, val)
    return (False, "", 0, 0)

def solvegrid(output: bool = False, outputargs = ["", False, False, False, False, "*"]):
    global grid
    global validdigs
    global remcoldigs
    global remrowdigs
    global remunitdigs

    start = grid.copy()
    steps = []

    resetgridparams()

    while not gridsolved():
        (success, dostep, celli, val) = applyrules(outputargs[5])

        if not success:
            if outputargs[3]:
                print("Failed to solve sudoku:", ("\n" if outputargs[4] else " "), getgridstr(start, outputargs[4]), sep="")
            return 1

        steps.append(dostep)

        grid[celli] = val

        updategridparams(celli)

    if output:
        if outputargs[0] == "":
            if outputargs[2]:
                print(getgridstr(start, outputargs[4]) + (" " if not outputargs[4] else "\n"), end="")

            print(getgridstr(grid, outputargs[4]), end="")

            if outputargs[1]:
                for step in steps:
                    print((" " if not outputargs[4] else "") + step, end="")
            print("")

        else:
            with open(outputargs[0], "a") as file:
                if outputargs[2]:
                    file.write(getgridstr(start, outputargs[4]) + (" " if not outputargs[4] else "\n"))

                file.write(getgridstr(grid, outputargs[4]))

                if outputargs[1]:
                    for step in steps:
                        file.write((" " if not outputargs[4] else "") + step)
                file.write("\n")


    return grid

def main():
    global grid

    args = sys.argv[1:]

    if not args:
        printhelp()
        return 0

    mainarg = ""

    outputfile = ""
    outputsteps = False
    outputstart = False
    formatboards = False
    allowedrules = allrules

    skipnext = False

    for i in range(0, len(args)):
        if skipnext:
            skipnext = False
            continue
        arg = args[i]

        if arg == "--output":
            if i == len(args):
                print("Invalid syntax: --output requires file")
                return 1

            outputfile = args[i + 1]
            skipnext = True
        elif arg == "--steps":
            outputsteps = True
        elif arg == "--start":
            outputstart = True
        elif arg == "--format":
            formatboards = True
        elif arg == "--allow":
            if i == len(args):
                print("Invalid syntax: --allow requires ruleset")
                return 1

            allowedrules = args[i + 1]
            skipnext = True
        elif arg == "--disallow":
            if i == len(args):
                print("Invalid syntax: --disallow requires ruleset")
                return 1

            for c in args[i + 1]:
                allowedrules = allowedrules.replace(c, "")
            skipnext = True
        elif arg == "-h" or arg == "--help":
            printhelp()
            return 0
        elif arg == "--rules":
            printrules()
            return 0;
        else:
            mainarg = arg.rstrip()
            break


    if allowedrules == allrules:
        allowedrules = "*"


    if os.path.isfile(mainarg):
        with open(mainarg, "r") as file:
            for line in file:

                setgrid(line.rstrip())
                if not validategrid(False):
                    continue

                solvegrid(True, [outputfile, outputsteps, outputstart, False, formatboards, allowedrules])

    else:
        setgrid(mainarg)
        if not validategrid(True):
            print("Couldn't parse ", mainarg)
            print("Invalid filename or grid")
            return 1

        solvegrid(True, [outputfile, outputsteps, outputstart, True, formatboards, allowedrules])




if __name__ == "__main__":
    main()