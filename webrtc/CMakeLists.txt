cmake_minimum_required(VERSION 3.21)
project(webrtc_chat LANGUAGES CXX)

include(FetchContent)

set(NO_MEDIA ON CACHE BOOL "Build data channels only" FORCE)
set(NO_WEBSOCKET ON CACHE BOOL "Disable unused WebSocket support" FORCE)
set(NO_EXAMPLES ON CACHE BOOL "Disable upstream examples" FORCE)
set(NO_TESTS ON CACHE BOOL "Disable upstream tests" FORCE)

FetchContent_Declare(
    libdatachannel
    GIT_REPOSITORY https://github.com/paullouisageneau/libdatachannel.git
    GIT_TAG v0.24.6
    GIT_SHALLOW TRUE
    GIT_SUBMODULES_RECURSE TRUE
)
FetchContent_MakeAvailable(libdatachannel)

add_executable(peer peer.cpp)
target_compile_features(peer PRIVATE cxx_std_17)
target_link_libraries(peer PRIVATE LibDataChannel::LibDataChannel)
