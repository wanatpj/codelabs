#include <iostream>


class Animal {
public:
    Animal() {
        std::cout << "I can eat." << std::endl;
    }
};

class TextIntelligence {
public:
    TextIntelligence() {
        std::cout << "I cat write." << std::endl;
    }
};

class Human : public Animal, public TextIntelligence {};

class GPTRobot : public TextIntelligence {};

int main () {
    std::cout << "Creating an Animal." << std::endl;
    Animal animal;
    std::cout << "Creating a TextIntelligence." << std::endl;
    TextIntelligence text_intelligence;
    std::cout << "Creating a Human." << std::endl;
    Human human;
    std::cout << "Creating a GPTRobot." << std::endl;
    GPTRobot gpt_robot;
    return 0;
}