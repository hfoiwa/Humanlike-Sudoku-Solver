import sys
import os

def printhelp():
    print("Usage: ", sys.argv[0], " <file|grid>")
    print("A  grid is 81 digits, 0 is used for empty cells")
    print("A file consists of lines of grids")
    print("")
    print("--output <file>    Outputs to file")
    print("--steps            Output steps along with solution")
    print("--start            Output starting grid along with solution")

    return 0

def validategrid(grid: str, printerr: bool = True):
    if len(grid) != 81:
        if printerr:
            print("Invalid grid: ", grid, "\nGrids must be 81 characters long")
        return False
    if not grid.isdigit():
        if printerr:
            print("Invalid grid: ", grid, "\nGrids must contain only digits")
        return False

    return True

def solvegrid(grid: str, output: bool = False, outputargs = ["", False, False]):

    start = grid
    steps = []


    if output:
        if outputargs[0] == "":
            if outputargs[2]:
                print(start + " ", end="")

            print(grid, end="")

            if outputargs[1]:
                for step in steps:
                    print(" " + step, end="")
            print("")

        else:
            with open(outputargs[0], "a") as file:
                if outputargs[2]:
                    file.write(start + " ")

                file.write(grid)

                if outputargs[1]:
                    for step in steps:
                        file.write(" " + step)
                file.write("\n")


    return grid

def main():

    args = sys.argv[1:]

    if not args:
        printhelp()
        return 0

    mainarg = ""

    outputfile = ""
    outputsteps = False
    outputstart = False

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
        else:
            mainarg = arg.rstrip()
            break

    if os.path.isfile(mainarg):
        with open(mainarg, "r") as file:
            for line in file:
                if not validategrid(line, False):
                    continue

                solvegrid(line, True, [outputfile, outputsteps, outputstart])

    elif validategrid(mainarg, True):
        solvegrid(mainarg, True, [outputfile, outputsteps, outputstart])

    else:
        print("Couldn't parse ", mainarg)
        print("Invalid filename or grid")
    







if __name__ == "__main__":
    main()