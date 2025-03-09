#!/bin/sh

command_exists() {
    command -v "$1" > /dev/null 2>&1
}

check_uv_dependency() {
    if ! command_exists "uv"; then
        printf "installing universal viewer...\n"
        curl -LsSf https://astral.sh/uv/install.sh | sh
        printf "universal viewer installed\n"
    else
        printf "universal viewer already installed\n"
        uv self update
    fi
}


print "checking dependencies...\n"
check_uv_dependency
echo "Version: $(uv --version)"
printf "dependencies checked\n"

if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    printf "Adding %s to PATH\n" "$HOME/.local/bin"
    export PATH="$HOME/.local/bin:$PATH"
    printf "Done. Please add the following line to your shell configuration file:\n"
    printf "export PATH=\$HOME/.local/bin:\$PATH\n"
fi
