#!/usr/bin/env bash
source $HOME/.gnuhealthrc

LANGUAGE=$@
## All languages which translation progress > 0
## https://hosted.weblate.org/projects/gnu-health/health/
ALL_LANGUAGES="ar es kab id tr sr_Cyrl el de it_IT ja_JP ka fr pl ht sv lo fi pt_BR ml uk zh_CN"
## Ignore all languages which translation progress = 0
IGNORE_LANGUAGES="ca hu eo ru kn ckb sq zh_Hant nb_NO"
TRYTON_DATABASE="po-export-db"
TRYTON_SERVER_DIR=${GNUHEALTH_DIR}/tryton/server
TRYTOND_ADMIN_CMD="${TRYTON_SERVER_DIR}/trytond-${TRYTON_VERSION}/bin/trytond-admin --email admin -d ${TRYTON_DATABASE} --all"

help()
{
    cat << EOF

GNU Health HMIS po files export tool

usage: `basename $0` LANG

    Example:
    $ bash ./po-export.sh zh_CN
    $ bash ./po-export.sh zh_CN ca
    $ bash ./po-export.sh --all

EOF
    exit 0
}

if [ $# -eq 0 ]; then
    help
fi

echo ""
echo "+--------------------------------------------+"
echo "|    GNU Health HMIS po files export tool    |"
echo "+--------------------------------------------+"
echo ""

if [[ $LANGUAGE = "--all" ]]; then
    LANGUAGE=${ALL_LANGUAGES}
fi
    
for lang in $LANGUAGE; do
    if ! [[ "$ALL_LANGUAGES" =~ "$lang" ]]; then
        echo "Error: '$lang' is not a value in '$ALL_LANGUAGES'!"
        exit 0
    fi
done

echo "## Export po files of '$LANGUAGE'."
echo ""

echo "## Creating database '${TRYTON_DATABASE}' ..."
dropdb --if-exists ${TRYTON_DATABASE} >/dev/null
createdb ${TRYTON_DATABASE}

echo "## Creating admin password file ..."
password_file=$(mktemp -t gnuhealth-tempfile.XXXXXX)
echo "gnuhealth" > "${password_file}"
export TRYTONPASSFILE="${password_file}"

echo "## Running trytond-admin command to update DB (1. Init setup) ..."
${TRYTOND_ADMIN_CMD}

modules_ignored="('health_icd10pcs','health_icd11')"
echo "## Active all modules with psql command，except $modules_ignored ..."
psql -q -c "UPDATE ir_module SET state = 'to activate' WHERE name NOT IN $modules_ignored" ${TRYTON_DATABASE}

echo "## Running trytond-admin command to update DB (2. Active modules) ..."
${TRYTOND_ADMIN_CMD}
psql -q -c "UPDATE ir_translation SET value = ''" ${TRYTON_DATABASE}

echo "## Add Language to tryton ..."
python3 po-export.py --user admin     \
        --database ${TRYTON_DATABASE} \
        --add-languages ${LANGUAGE}

echo "## Running trytond-admin command to update DB (3. Active language) ..."
## If we do not run this step, the existing translations of LANGUAGE
## will be not merged, we just get pot template.
${TRYTOND_ADMIN_CMD} --language ${LANGUAGE}

echo "## Export po files ..."
## we always recreate db in po-export.sh, but we need to use
## --run-cleanup-step argument, the problem is that it is very very
## slow when export all languages.
python3 po-export.py --user admin     \
        --database ${TRYTON_DATABASE} \
        --run-cleanup-step            \
        --export-pot                  \
        --export-languages ${LANGUAGE} 
