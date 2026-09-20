#!/usr/bin/env bash
set -euo pipefail

if [[ "$(uname -s)" != "Darwin" ]] || ! command -v security >/dev/null 2>&1; then
	printf 'This helper requires macOS Keychain.\n' >&2
	exit 1
fi

store_password() {
	local service_name="$1"
	local prompt="$2"
	local password
	printf '%s: ' "$prompt"
	read -rs password
	printf '\n'
	if [[ -z "$password" ]]; then
		printf '%s cannot be empty.\n' "$prompt" >&2
		exit 1
	fi
	security add-generic-password -U -a root -s "$service_name" -w "$password" >/dev/null
	unset password
}

if [[ "${1:-}" == "--tdengine-only" ]]; then
	store_password jd-energy-tdengine 'TDengine password'
	printf 'TDengine credential updated in macOS Keychain.\n'
	exit 0
fi

printf 'Jump host SSH password: '
read -rs jump_password
printf '\n'
if [[ -z "$jump_password" ]]; then
	printf 'Jump host SSH password cannot be empty.\n' >&2
	exit 1
fi

printf 'Site SSH password: '
read -rs site_password
printf '\n'
if [[ -z "$site_password" ]]; then
	printf 'Site SSH password cannot be empty.\n' >&2
	exit 1
fi

printf 'TDengine password: '
read -rs tdengine_password
printf '\n'
if [[ -z "$tdengine_password" ]]; then
	printf 'TDengine password cannot be empty.\n' >&2
	exit 1
fi

security add-generic-password -U -a root -s jd-energy-vpn-jump -w "$jump_password" >/dev/null
security add-generic-password -U -a root -s jd-energy-vpn-site -w "$site_password" >/dev/null
security add-generic-password -U -a root -s jd-energy-tdengine -w "$tdengine_password" >/dev/null
unset jump_password site_password tdengine_password

printf 'VPN credentials saved in macOS Keychain.\n'