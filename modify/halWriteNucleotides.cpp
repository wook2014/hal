// Hacky script to allow writing to a genome's sequence from a TSV (probably
// after an ancestorsML run).
#include "hal.h"
#include "halAlignmentInstance.h"
#include <fstream>

using namespace hal;
using namespace std;

static void initParser(CLParser &optionsParser) {
    optionsParser.setDescription("Write changes to a hal sequence from a TSV "
                                 "containing fields "
                                 "genomeName\tpos\toldChar\tnewChar. Note that "
                                 "the position is in genome coordinates!");
    optionsParser.addArgument("inFile", "hal file");
    optionsParser.addArgument("tsvFile", "tsv file");
}

int main(int argc, char *argv[]) {
    CLParser optionsParser(WRITE_ACCESS);
    initParser(optionsParser);
    string inPath, tsvFile;
    try {
        optionsParser.parseOptions(argc, argv);
        inPath = optionsParser.getArgument<string>("inFile");
        tsvFile = optionsParser.getArgument<string>("tsvFile");
    } catch (exception &e) {
        optionsParser.printUsage(cerr);
        return 1;
    }
    AlignmentPtr alignment(openHalAlignment(inPath, &optionsParser,
                                            READ_ACCESS | WRITE_ACCESS));

    ifstream tsv(tsvFile.c_str());
    string line;
    int64_t lineNum = 0;
    while (getline(tsv, line)) {
        stringstream lineStream(line);
        string genomeName;
        hal_index_t pos;
        char prevChar, newChar;

        lineNum++;
        if (lineNum % 100000 == 0) {
            cout << lineNum << endl;
        }
        lineStream >> genomeName;
        lineStream >> pos;
        lineStream >> prevChar;
        lineStream >> newChar;
        Genome *genome = alignment->openGenome(genomeName);
        DnaIteratorPtr dnaIt = genome->getDnaIterator(pos);
        if (fastUpper(dnaIt->getBase()) != prevChar) {
            dnaIt->toReverse();
            if (fastUpper(dnaIt->getBase()) != prevChar) {
                throw hal_exception("previous nucleotide " + string(1, dnaIt->getBase()) + " does not match expected " +
                                    string(1, prevChar) + "! Aborting early. Your hal file could be invalid now.");
            }
        }

        dnaIt->setBase(newChar);
    }
    tsv.close();
    alignment->close();
    return 0;
}
