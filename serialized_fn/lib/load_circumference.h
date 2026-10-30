#pragma once

class CircumferenceLibrary {
public:
    using Circumference = double (*)(int);

    explicit CircumferenceLibrary(const char* filename);
    ~CircumferenceLibrary();

    CircumferenceLibrary(const CircumferenceLibrary&) = delete;
    CircumferenceLibrary& operator=(const CircumferenceLibrary&) = delete;

public:
    Circumference circumference = nullptr;
private:
    void* library_ = nullptr;
};
