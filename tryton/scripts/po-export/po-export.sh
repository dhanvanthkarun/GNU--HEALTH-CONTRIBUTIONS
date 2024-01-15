#!/usr/bin/env bash
source $HOME/.gnuhealthrc

LANGUAGE=$@
## All languages which translation progress > 10%
## https://hosted.weblate.org/projects/gnu-health/health/
ALL_LANGUAGES="ar es kab id tr sr_Cyrl sv el de it_IT ja_JP ka fr lo pt_BR zh_CN"
## Ignore all languages which translation progress <= 10%, If somebody
## are maintaining a language, he can ask to update ALL_LANGUAGE and
## IGNORE_LANGUAGE when progress > 10%
IGNORE_LANGUAGES="ca hu eo ru kn ckb sq zh_Hant nb_NO pl ht ml uk fi"
TRYTON_DATABASE="po-export-db"
TRYTON_SERVER_DIR=${GNUHEALTH_DIR}/tryton/server
TRYTOND_ADMIN_CMD="${TRYTON_SERVER_DIR}/trytond-${TRYTON_VERSION}/bin/trytond-admin --email admin -d ${TRYTON_DATABASE} --all"

PO_EXPORT_DIR=$(dirname "$(realpath "${BASH_SOURCE[0]}")")
cd ${PO_EXPORT_DIR}

if [[ ! -f "po-export.py" ]]; then
 　　echo "Error: po-export.py is not found at directory: ${PO_EXPORT_DIR}!"
     exit 0
fi

help()
{
    cat << EOF

GNU Health HMIS po files export tool.

Usage:

    $ bash ./`basename $0` LANG

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

if [[ $LANGUAGE = "--all" ]]; then
    LANGUAGE=${ALL_LANGUAGES}
fi
    
for lang in $LANGUAGE; do
    if ! [[ "$ALL_LANGUAGES" =~ "$lang" ]]; then
        echo "Error: '$lang' is not a value in '$ALL_LANGUAGES'!"
        exit 1
    fi
done

echo ""
echo "+--------------------------------------------+"
echo "|    GNU Health HMIS po files export tool    |"
echo "+--------------------------------------------+"
echo ""

cat << EOF

NOTE: If your are gnuhealth developer, before export po files, suggest
do the following steps, which can reduce po files merge conflicts.

1. Commit all pending changes in weblate.
    
   a) Open url in web browser: https://hosted.weblate.org/projects/gnu-health/
   b) Click button: Manage > Repository maintenance > (pending changes) Commit
   c) Make sure commits can be found at: https://hg.weblate.org/gnu-health/health
   
2. Lock translation in weblate.

   Click button: Manage > Repository maintenance > Lock

3. Pull and merge changes in below hg repos to local repo your are
   working.

   1. gnuhealth-upstream: https://hg.savannah.gnu.org/hgweb/health
   2. gnuhealth-weblate:  https://hg.weblate.org/gnu-health/health

EOF

read -p "Continue run po-export.sh? [y|n]" -n 1 -r
echo ""
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    exit 1
fi

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
## We always recreate $TRYTON_DATABASE database in po-export.sh, but
## --run-cleanup-step argument is required, this argument let
## po-export.py run slower a bit, for example: export 15 languages
## need about 2900s in my work machine.
python3 po-export.py --user admin     \
        --database ${TRYTON_DATABASE} \
        --run-cleanup-step            \
        --export-pot                  \
        --export-languages ${LANGUAGE} 


cat << EOF

After po-export.sh run successful and po files changes has been pushed
to gnuhealth upstream hg repo, we should:

1. Make sure all po files changes sync to weblate:

   a) Open url in web browser: https://hosted.weblate.org/projects/gnu-health/
   b) Click button: Manage > Repository maintenance > (missing commits) Push
   c) Make sure commits can be found at: https://hg.weblate.org/gnu-health/health

2. Unlock translation in weblate.

   Click button: Manage > Repository maintenance > Unlock

EOF
