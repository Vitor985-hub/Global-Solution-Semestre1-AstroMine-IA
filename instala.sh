#!/usr/bin/env bash

set -e

sourced=0
finish() {
	code="$1"
	if [ "$sourced" -eq 1 ]; then
		return "$code"
	fi
	exit "$code"
}

if [ -n "${ZSH_EVAL_CONTEXT:-}" ]; then
	case "$ZSH_EVAL_CONTEXT" in
		*:file) sourced=1 ;;
	esac
elif [ -n "${BASH_VERSION:-}" ] && [ "${BASH_SOURCE[0]}" != "$0" ]; then
	sourced=1
fi

if [ "$sourced" -ne 1 ]; then
	echo "Para manter o ambiente virtual ativo no terminal atual, execute: source ./instala.sh"
	exit 1
fi

echo "Criando ambiente virtual Python..."

if ! command -v py >/dev/null 2>&1; then
	echo "Erro: py nao foi encontrado no sistema."
	finish 1
fi

py -3.13 -m venv .venv

echo "Ambiente virtual criado em .venv"
echo "Ativando ambiente virtual da .venv para instalar dependencias..."
source .venv/Scripts/activate
echo "Instalando dependencias automaticamente..."

if [ ! -f requirement.txt ]; then
	echo "Erro: requirement.txt nao foi encontrado na raiz do projeto."
	finish 1
fi

py -m pip install --upgrade pip
py -m pip install -r requirement.txt

echo "Dependencias instaladas com sucesso"
echo "Ambiente virtual mantido ativo no terminal atual"
