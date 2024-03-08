#!/usr/bin/env bash

# SPDX-FileCopyrightText: 2008-2024 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2024 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

source $HOME/.gnuhealthrc

## We split languages to three groups, because if too many languages
## are processed at once, the speed is very very slow, at the moment,
## deal with a group need about 1 hour in my machine.
##
## LANG_GROUP1: The translation progress is relatively high,
## translation is more active. see:
## https://hosted.weblate.org/projects/gnu-health/health/
LANG_GROUP1="ar es kab id tr sr_Cyrl sv el de it_IT ja_JP ka fr lo pt_BR zh_CN"
## LANG_GROUP2: The translation progress is relatively low,
## translation is not very active.
LANG_GROUP2="ca hu eo ru kn ckb sq sl nl zh_Hant nb_NO pl ht ml uk fi"
## LANG_GROUP3: Reserved for future use.
LANG_GROUP3=""
ALL_LANGUAGES="${LANG_GROUP1} ${LANG_GROUP2} ${LANG_GROUP3}" 

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

    $ bash ./`basename $0` --lang LANG
    $ bash ./`basename $0` --group1
    $ bash ./`basename $0` --group2
    $ bash ./`basename $0` --group3

Example:

    $ bash ./po-export.sh --lang zh_CN
    $ bash ./po-export.sh --lang zh_CN ca

EOF
    exit 0
}

if [ $# -eq 0 ]; then
    help
fi

case $1 in
    --lang) LANGUAGE=$@;;
    --group1) LANGUAGE=${LANG_GROUP1};;
    --group2) LANGUAGE=${LANG_GROUP2};;
    --group3) LANGUAGE=${LANG_GROUP3};;
    help) help;;
    *) echo $1: Unrecognized argument; exit 1;;
esac

LANGUAGE=${LANGUAGE//--lang }

for lang in $LANGUAGE; do
    if ! [[ "${ALL_LANGUAGES}" =~ "$lang" ]]; then
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

NOTE for developer:

## Before run po-export.sh, the following steps can reduce po files merge conflicts.
1. Open GNU Health weblate page: (https://hosted.weblate.org/projects/gnu-health/)
2. Lock translation: (Manage > Repository maintenance > Lock)
3. Commit pending changes: (Manage > Repository maintenance > (pending changes) Commit)
4. Push outgoing commits: (Manage > Repository maintenance > Push)
5. Pull and update changes from gnuhealth upstream repo to your working repo.

## After run po-export.sh: 
1. Push po files changes to GNU Health upstream repo.
2. Open GNU Health weblate page: (https://hosted.weblate.org/projects/gnu-health/)
3. Sync all changes to weblate: (Manage > Repository maintenance > (missing commits) Update)
4. Unlock translation (Manage > Repository maintenance > Unlock)

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


source ./po-msguniq.sh
