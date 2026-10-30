#include "load_circumference.h"

#include <dlfcn.h>
#include <stdexcept>

using namespace std;

CircumferenceLibrary::CircumferenceLibrary(const char* filename) {
    library_ = dlopen(filename, RTLD_NOW);
    if (!library_)
        throw runtime_error(dlerror());

    dlerror();
    circumference = reinterpret_cast<Circumference>(
        dlsym(library_, "circumference"));

    if (const char* error = dlerror()) {
        runtime_error exception(error);
        dlclose(library_);
        throw exception;
    }
}

CircumferenceLibrary::~CircumferenceLibrary() {
    dlclose(library_);
}
