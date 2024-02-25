;;; gnuhealth-pot-fill.el --- A tool used to fill GNU Health pot file  -*- lexical-binding: t; -*-

;; Author: Feng Shu <tumashu@163.com>
;; Url: https://hg.savannah.gnu.org/hgweb/health/
;; Version: 0.0.1
;; Keywords: po, utils

;;; License:

;; This program is free software; you can redistribute it and/or modify
;; it under the terms of the GNU General Public License as published by
;; the Free Software Foundation, either version 3 of the License, or
;; (at your option) any later version.

;; This program is distributed in the hope that it will be useful,
;; but WITHOUT ANY WARRANTY; without even the implied warranty of
;; MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
;; GNU General Public License for more details.

;; You should have received a copy of the GNU General Public License
;; along with this program.  If not, see <http://www.gnu.org/licenses/>.

;;; Commentary:

;; This package is useful to fill pot files of GNU Health modules:

;; 1. health_icd10
;; 2. health_icd9procs

;; There are many strings need to translate in health_icd10 and
;; health_icd9procs modules, the context of pot files is like below:

;;     msgctxt "model:gnuhealth.pathology,name:A00"
;;     msgid "Cholera"
;;     msgstr ""

;; If the below data is found, for example:

;;     class	code	desc-translation
;;     icd10-disease	A00	霍乱

;; We can use this Emacs package to fill pot files to get a po file,
;; in following steps:

;; 1. Find the translated version of icd10 and icd9procs, in most
;;    case, we can find two xlsx files.
;; 2. Extract infos from xlsx files and update data/icd10-*.txt and
;;    icd9procs.txt
;; 3. Add to ~/.emacs
;;
;;    (add-to-list 'load-path "/PATH/TO/health/tryton/script/health-pot-fill")
;;    (require 'gnuhealth-po-update)
;;
;; 4. Open file with Emacs: health/tryton/health_icd10/locale/health_icd10.pot
;; 5. Run Emacs command (M-x): gnuhealth-pot-fill
;; 6. Save file to zh_CN.po.
;; 7. Review diff with the help of hg (This step is very import!!!).

;;; Code:
(defun gnuhealth-pot-fill ()
  (interactive)
  (let ((module (completing-read
                 "GNU Health module:"
                 '(health_icd10 health_icd9procs)))
        (elfile (or (locate-library "gnuhealth-pot-fill.el")
                    (read-file-name "gnuhealth-pot-fill.el file:"))))
    (when elfile
      (let* ((dir (file-name-directory elfile))
             (icd10-chapter (expand-file-name "data/icd10-chapter.txt" dir))
             (icd10-section (expand-file-name "data/icd10-section.txt" dir))
             (icd10-disease (expand-file-name "data/icd10-disease.txt" dir))
             (icd9procs (expand-file-name "data/icd9procs.txt" dir))
             (records (split-string
                       (with-temp-buffer
                         (cond ((equal module "health_icd9procs")
                                (insert-file-contents icd9procs))
                               ((equal module "health_icd10")
                                (insert-file-contents icd10-chapter)
                                (insert-file-contents icd10-section)
                                (insert-file-contents icd10-disease))
                               (t nil))
                         (buffer-string))
                       "\n+")))
        (dolist (record records)
          (gnuhealth--handle-record record))
        (message "gnuhealth-pot-fill is finished.")))))

(defun gnuhealth--handle-record (record)
  (let* ((content (split-string record "	+"))
         (class (nth 0 content))
         (code (nth 1 content))
         (desc (nth 2 content))
         (func (intern (format "gnuhealth--handle-%s" class))))
    (when (> (length class) 0)
      (if (not (functionp func))
          (message "WARN: class %s is invaild!!!" class)
        (message "Filling %s: %s %s ..." class code desc)
        (funcall func code desc)))))

(defun gnuhealth--handle-icd10-disease (code desc)
  (goto-char (point-min))
  (when (and (re-search-forward
              (format "pathology,name:%s\""
                      (replace-regexp-in-string
                       "[+*.]" "" code))
              nil t)
             (re-search-forward "msgstr \"" nil t))
    (delete-region (point) (line-end-position))
    (insert desc)
    (insert "\"")
    (gnuhealth--remove-useless-msgstr-lines))
  (goto-char (point-min)))

(defun gnuhealth--remove-useless-msgstr-lines ()
  (let ((end (save-excursion (re-search-forward "msgctxt \"" nil t))))
    (when end
      (delete-region (point) end)
      (insert "\n\nmsgctxt \""))))

(defun gnuhealth--handle-icd10-section (code desc)
  (goto-char (point-min))
  (when (and (re-search-forward (format "\"(%s)" code) nil t)
             (re-search-forward "msgstr \"" nil t))
    (delete-region (point) (line-end-position))
    (insert (format "(%s) %s" code desc))
    (insert "\"")
    (gnuhealth--remove-useless-msgstr-lines))
  (goto-char (point-min)))

(defun gnuhealth--handle-icd10-chapter (code desc)
  (goto-char (point-min))
  (when (and (re-search-forward
              (format "category,name:icdcat%s\"" code)
              nil t)
             (re-search-forward "msgstr \"" nil t))
    (delete-region (point) (line-end-position))
    (insert (format "第%s章 %s" code desc))
    (insert "\"")
    (gnuhealth--remove-useless-msgstr-lines))
  (goto-char (point-min)))

(defun gnuhealth--handle-icd9procs (code desc)
  (goto-char (point-min))
  (when (and (re-search-forward
              (format "procedure,description:cie9_%s\""
                      (replace-regexp-in-string
                       "[.]" "-" code))
              nil t)
             (re-search-forward "msgstr \"" nil t))
    (delete-region (point) (line-end-position))
    (insert desc)
    (insert "\"")
    (gnuhealth--remove-useless-msgstr-lines))
  (goto-char (point-min)))

(provide 'gnuhealth-pot-fill)
