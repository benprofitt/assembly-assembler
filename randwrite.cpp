//
//  randwrite.cpp
//  
//
//  Created by Ben Parfitt on 5/10/17.
//
//

#include <iostream>
#include <cstdlib>
#include <fstream>
#include <assert.h>
#include "list.h"

using namespace std;

// This is used to ensure the length and seed length arguments are numbers.
bool isNum(string num)
{
    // The loop counts through the length of the string input.
    for (size_t index = 0; index < num.length(); index++) {
        bool character = false;
        // This loop checks if the chars are numbers.
        for (char count = '0'; count <= '9' && character == false; count++)
            if (num[index] == count)
                character = true;
        // If the chars aren't nums, return false.
        if (character == false)
            return false;
    }
    // Else, return true.
    return true;
}

// Here we make the new seed.
string makeSeed(const list & sList, size_t sLength)
{
    // We pick the starting position for the new seed.
    size_t seedPos = rand() % (sList.size()-sLength);
    string seed = "";
    
    // Add all letters of the new seed to a string.
    for (size_t index = 0; index < sLength; ++index) {
        seed += sList.get(seedPos + index);
    }
    // Return the seed.
    return seed;
}

// Makes a list of all the letters directly after the seed.
void seedList(const list & sList, string & seed, size_t sLen, list & seedLetter)
{
    // Runs a loop through the source list to find the first letter of the seed.
    for (size_t index = 0; index < sList.size() - 1 - sLen; ++index)
        if (sList.get(index) == seed[0]){
            size_t count = 1;
            // If the first letter is found, the check for rest of the seed.
            while (seed[count] == sList.get(index + count) && count < sLen){
                count++;
                // If the seed is present, add the char following to the list.
                if (count == sLen)
                    seedLetter.add(sList.get(index + count), 0);
            }
        }
}

// Makes the new seed from the old seed
void newSeedMake(const list & sList, string & seed, size_t sLen)
{
    // Handles the case where the seed is of length 0.
    if (sLen == 0){
        seed += sList.get(rand() % (sList.size()));
        return;
    }
    
    // Initializes the list to hold the possible new letters.
    list seedLetter;
    // Makes the list of all possible new lettters.
    seedList(sList, seed, sLen, seedLetter);
    
    // If the list is empty, make a new seed.
    if (seedLetter.size() == 0) {
        seed = makeSeed(sList, sLen);
        newSeedMake(sList, seed, sLen);
    }
    // Else choose the new letter at random, and alter the seed.
    else
        seed += seedLetter.get(rand() % (seedLetter.size()));
}

int main(int argc, char **argv)
{
    // Returns an error if there are not 5 arguments, and terminates.
    if (argc != 5){
        cout << "Invalid number of arguments!" << endl;
        return -1;
    }
    
    // Creates the list that the source will be stored in.
    list charList;
    
    // Identifies the input source file from the inputs.
    ifstream infile(argv[3]);
    if (!infile.is_open()){
        cout << "Invalid input file!" << endl;
        return -1;
    }
    
    // Adds all characters from the input to a list as ints.
    int ch;
    while ((ch = infile.get()) != EOF)
        charList.add(ch, charList.size());
    
    // Returns error message if the source is empty, and terminates.
    if (charList.size() == 0){
        cout << "Invalid input file!" << endl;
        return -1;
    }
    
    // Checks if the seed and file length inputs are numbers.
    if (!isNum(argv[1]) || !isNum(argv[2])){
        cout << "Invalid arguments!" << endl;
        return -1;
    }
    
    int seedLength = atoi(argv[1]);
    
    // Returns error message if the seed should be longer than the source,
    // or the seeed is negative, and terminates.
    if (int(charList.size()) <= seedLength || seedLength < 0){
        cout << "Invalid seed length!" << endl;
        return -1;
    }
    
    // Makes an initial seed.
    string seed = makeSeed(charList, atoi(argv[1]));
    
    // Selects the output location.
    ofstream outfile(argv[4]);
    
    if (!outfile.is_open()){
        cout << "Invalid output file!" << endl;
        return -1;
    }
    
    // Initializes a counter for thhe while loop below
    int counter = 0;
    
    // While the file being written is shorter than the desired length,
    // the program will make new seeds, and add the new character to
    // the file with each new seed. Deletes the first letter of the seed.
    while (counter < atoi(argv[2])) {
        newSeedMake(charList, seed, seedLength);
        outfile.put(seed[atoi(argv[1])]);
        seed.erase(0,1);
        counter++;
    }
    return 0;
}
