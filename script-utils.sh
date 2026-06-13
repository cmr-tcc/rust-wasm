#!/bin/bash

echo_color() {
    local text="$1"
    local color="$2"

    case "$color" in
        --red)     code="31" ;;
        --green)   code="32" ;;
        --yellow)  code="33" ;;
        --blue)    code="34" ;;
        --magenta) code="35" ;;
        --cyan)    code="36" ;;
        *)         code="0" ;;
    esac

    printf "\033[%sm%s\033[0m\n" "$code" "$text"
}