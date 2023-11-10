#/bin/bash
rm -rf tapenade
git clone --depth 1 https://gitlab.inria.fr/tapenade/tapenade.git
cd tapenade
./gradlew clean
javac -version
./gradlew