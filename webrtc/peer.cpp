#include <rtc/rtc.hpp>

#include <atomic>
#include <chrono>
#include <condition_variable>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <mutex>
#include <stdexcept>
#include <string>
#include <thread>

using namespace std;
using namespace std::chrono_literals;

struct Connection {
    mutex mutex;
    condition_variable changed;
    shared_ptr<rtc::DataChannel> channel;
    bool gatheringComplete = false;
    bool channelOpen = false;
    bool failed = false;
};

void configureChannel(const shared_ptr<rtc::DataChannel>& channel,
                      Connection& connection) {
    channel->onOpen([&connection] {
        {
            lock_guard<mutex> lock(connection.mutex);
            connection.channelOpen = true;
        }
        cerr << "Data channel is open. Type a message; /quit exits.\n> " << flush;
        connection.changed.notify_all();
    });

    channel->onMessage([](rtc::message_variant message) {
        if (const auto* text = get_if<string>(&message)) {
            cerr << "\npeer: " << *text << "\n> " << flush;
        }
    });
}

void waitForGathering(rtc::PeerConnection& peer, Connection& connection) {
    unique_lock<mutex> lock(connection.mutex);
    if (!connection.changed.wait_for(lock, 60s, [&connection] {
            return connection.gatheringComplete || connection.failed;
        })) {
        throw runtime_error("timed out gathering ICE candidates");
    }
    if (connection.failed) {
        throw runtime_error("peer connection failed while gathering ICE candidates");
    }

    const auto description = peer.localDescription();
    if (!description) {
        throw runtime_error("local SDP is not available");
    }

    cout << "BEGIN_SDP\n" << *description << "\nEND_SDP\n" << flush;
}

string readDescription(const string& kind) {
    cerr << "Paste the remote " << kind
         << " SDP, including BEGIN_SDP and END_SDP lines:\n";

    string line;
    string description;
    bool reading = false;
    while (getline(cin, line)) {
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        if (line == "BEGIN_SDP") {
            reading = true;
            continue;
        }
        if (line == "END_SDP" && reading) {
            return description;
        }
        if (reading) {
            description += line + "\r\n";
        }
    }
    throw runtime_error("input ended before END_SDP");
}

rtc::Configuration readConfiguration(int argc, char** argv) {
    rtc::Configuration config;
    if (argc >= 3) {
        config.iceServers.emplace_back(argv[2]);
    }
    if (argc == 7) {
        config.iceServers.emplace_back(
            argv[3], static_cast<uint16_t>(stoi(argv[4])), argv[5], argv[6]);
    }
    return config;
}

int main(int argc, char** argv) try {
    if (argc != 2 && argc != 3 && argc != 7) {
        cerr << "Usage: peer offer|answer [stun:host:port] "
                "[turn-host turn-port turn-user turn-password]\n";
        return 2;
    }

    const string role = argv[1];
    if (role != "offer" && role != "answer") {
        throw invalid_argument("role must be 'offer' or 'answer'");
    }

    rtc::InitLogger(rtc::LogLevel::Warning);
    rtc::PeerConnection peer(readConfiguration(argc, argv));
    Connection connection;

    peer.onGatheringStateChange([&connection](rtc::PeerConnection::GatheringState state) {
        if (state == rtc::PeerConnection::GatheringState::Complete) {
            {
                lock_guard<mutex> lock(connection.mutex);
                connection.gatheringComplete = true;
            }
            connection.changed.notify_all();
        }
    });

    peer.onStateChange([&connection](rtc::PeerConnection::State state) {
        cerr << "Peer connection: " << state << '\n';
        if (state == rtc::PeerConnection::State::Failed) {
            {
                lock_guard<mutex> lock(connection.mutex);
                connection.failed = true;
            }
            connection.changed.notify_all();
        }
    });

    if (role == "offer") {
        connection.channel = peer.createDataChannel("chat");
        configureChannel(connection.channel, connection);

        peer.setLocalDescription(rtc::Description::Type::Offer);
        cerr << "Gathering ICE candidates...\n";
        waitForGathering(peer, connection);

        const string answer = readDescription("answer");
        peer.setRemoteDescription(rtc::Description(answer, "answer"));
    } else {
        peer.onDataChannel([&connection](shared_ptr<rtc::DataChannel> channel) {
            {
                lock_guard<mutex> lock(connection.mutex);
                connection.channel = channel;
            }
            configureChannel(channel, connection);
        });

        const string offer = readDescription("offer");
        peer.setRemoteDescription(rtc::Description(offer, "offer"));
        peer.setLocalDescription(rtc::Description::Type::Answer);
        cerr << "Gathering ICE candidates...\n";
        waitForGathering(peer, connection);
    }

    {
        unique_lock<mutex> lock(connection.mutex);
        if (!connection.changed.wait_for(lock, 60s, [&connection] {
                return connection.channelOpen || connection.failed;
            })) {
            throw runtime_error("timed out waiting for the data channel; check ICE/STUN/TURN and firewalls");
        }
        if (connection.failed) {
            throw runtime_error("peer connection failed");
        }
    }

    string message;
    while (getline(cin, message)) {
        if (message == "/quit") {
            break;
        }
        lock_guard<mutex> lock(connection.mutex);
        if (connection.channel && connection.channel->isOpen()) {
            connection.channel->send(message);
        }
        cerr << "> " << flush;
    }
    return 0;
} catch (const exception& error) {
    cerr << "Error: " << error.what() << '\n';
    return 1;
}
