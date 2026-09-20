#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

export VPN_JUMP_HOST="${VPN_JUMP_HOST:-8.216.40.206}"
export VPN_JUMP_USERNAME="${VPN_JUMP_USERNAME:-root}"
export VPN_SITE_USERNAME="${VPN_SITE_USERNAME:-root}"
export TDENGINE_USERNAME="${TDENGINE_USERNAME:-root}"

read_keychain_password() {
	local service_name="$1"
	security find-generic-password -a root -s "$service_name" -w 2>/dev/null || true
}

if [[ "$(uname -s)" == "Darwin" ]]; then
	export VPN_JUMP_PASSWORD="${VPN_JUMP_PASSWORD:-$(read_keychain_password jd-energy-vpn-jump)}"
	export VPN_SITE_PASSWORD="${VPN_SITE_PASSWORD:-$(read_keychain_password jd-energy-vpn-site)}"
	export TDENGINE_PASSWORD="${TDENGINE_PASSWORD:-$(read_keychain_password jd-energy-tdengine)}"
fi

required_vpn_vars=(
	VPN_JUMP_HOST
	VPN_JUMP_USERNAME
	VPN_JUMP_PASSWORD
	VPN_SITE_USERNAME
	VPN_SITE_PASSWORD
	TDENGINE_USERNAME
	TDENGINE_PASSWORD
)

missing_vars=()
for variable_name in "${required_vpn_vars[@]}"; do
	if [[ -z "${!variable_name:-}" ]]; then
		missing_vars+=("$variable_name")
	fi
done

if (( ${#missing_vars[@]} > 0 )); then
	printf 'Missing required VPN environment variables:\n' >&2
	printf '  %s\n' "${missing_vars[@]}" >&2
	if [[ "$(uname -s)" == "Darwin" ]]; then
		printf 'Run ./configure_vpn_keychain.sh once to store credentials securely.\n' >&2
	fi
	exit 1
fi

if [[ ! -x .venv/bin/uvicorn ]]; then
	printf 'Missing backend/.venv. Create it and install requirements first.\n' >&2
	exit 1
fi

exec .venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
