# -*- coding: utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2014 BigML
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

"""Tree level output for R

This module defines functions that generate R code to make local
predictions
"""
import sys

from bigml.tree_utils import (
    to_camel_js, sort_fields, docstring_comment,
    INDENT, MAX_ARGS_LENGTH, TERM_OPTIONS, ITEM_OPTIONS)

from bigml.model import Model
from bigmler.export.out_tree.rtree import RTree

def dot(name):
    """Creates a dot-separated name

    """
    return name.replace(" ", ".")


class RModel(Model):

    def __init__(self, model, api=None, fields=None):
        """Empty attributes to be overriden

        """
        self.tree_class = RTree
        Model.__init__(self, model, api, fields)

    def plug_in(self, out=sys.stdout, filter_id=None, subtree=True):
        """Writes an R function that implements the model.

        """


    def plug_in(self, out=sys.stdout, hadoop=False,
                filter_id=None, subtree=True):
        """Returns a basic javascript implementation of local predictions

        `out` is file descriptor to write the javascript code.

        """
        # fill the dotted variable names with the R_KEYWORDS restrictions
        objective_field = self.tree.fields[self.tree.objective_id]
        camelcase = to_camel_js(objective_field['name'], False)
        objective_field['CamelCase'] = camelcase
        default = "NA"
        args = []
        for field in [(key, val) for key, val in
                      sort_fields(self.tree.fields)]:
            field_obj = self.tree.fields[field[0]]
            field_obj['dotted'] = dot(field_obj['name'])
            args.append("%s=%s" % (field_obj['dotted'], default))

        body, term_analysis_predicates, item_analysis_predicates = \
            self.tree.plug_in_body()
        terms_body = ""
        items_body = ""
        if term_analysis_predicates:
            terms_body = self.r_term_analysis_body(term_analysis_predicates)
        if item_analysis_predicates:
            items_body = self.r_item_analysis_body(item_analysis_predicates)

        predictor_definition = (u"predict%s <- function" %
                                camelcase)
        depth = len(predictor_definition) + 1
        predictor = u"%s(%s){\n" % (predictor_definition,
                                   (",\n" + " " * depth).join(args))
        join_str = "\n#"
        docstring = join_str.join(self.docstring().split("\n"))
        predictor_doc = (u"# " + docstring +
                         u"\n" + u"#\n")
        output = predictor_doc + predictor
        output += terms_body + items_body + body
        output += u"%sreturn(NA);\n}\n" % INDENT
        out.write(output)
        out.flush()

    def r_term_analysis_body(self, term_analysis_predicates):
        """ Writes auxiliary functions to handle the term analysis fields

        """
        term_analysis_options = set(map(lambda x: x[0],
                                        term_analysis_predicates))
        term_analysis_predicates = set(term_analysis_predicates)

        body = u""
        # static content
        body += """
    TERM_ANALYSIS <- list("""
        lines = []
        for field_id in term_analysis_options:
            inner_lines = []
            field = self.tree.fields[field_id]
            lines.append("""
        \"%s\"=list(""" % field['dotted'])
            for option in field['term_analysis']:
                if option in TERM_OPTIONS:
                    value = repr(field['term_analysis'][option])
                    value = value if not value.startswith("u") else value[1:]
                    if value == 'True':
                        value = 'TRUE'
                    elif value == 'False':
                        value = 'FALSE'
                    inner_lines.append("""
                \"%s\"= %s""" % (option, value))
            lines[-1] = lines[-1] +  ",\n".join(inner_lines)
        lines[-1] = lines[-1] + """
        )"""
        body += ",\n".join(lines) + """
    )"""

        if term_analysis_predicates:
            term_forms = {}
            fields = self.tree.fields
            for field_id, term in term_analysis_predicates:
                alternatives = []
                field = fields[field_id]
                if field['dotted'] not in term_forms:
                    term_forms[field['dotted']] = {}
                all_forms = field['summary'].get('term_forms', {})
                if all_forms:
                    alternatives = all_forms.get(term, [])
                    if alternatives:
                        terms = [term]
                        terms.extend(all_forms.get(term, []))
                        term_forms[field['dotted']][term] = terms

            body += """
    TERM_FORMS <- list("""
            lines = []
            for field in term_forms:
                inner_lines = []
                lines.append("""
        \"%s\"=list(""" % field)
                for term in term_forms[field]:
                    inner_lines.append("""
            \"%s\"=%s""" % (encode(term, "utf-8"),
                            encode(term_forms[field][term], "utf-8")))
                lines[-1] = lines[-1] + ",\n".join(inner_lines)
            lines[-1] = lines[-1] + """
        )"""
            body += ",\n".join(lines) + """
    )
"""
        body += """
    TM_TOKENS <- "tokens_only"
    TM_FULL_TERM <- "full_terms_only"
    TM_ALL <- "all"
    FULL_TERM_PATTERN <- '^.+\\\\b.+$'

    termMatches <- function (text, fieldLabel, term) {

      # Computes term matches depending on the chosen text analysis options
      #
      # @param {string} text Input text
      # @param {string} fieldLabel Name of the field
      # @param {string} term Term to compare

      if (is.na(text))
        return(0)
      options <- TERM_ANALYSIS[[fieldLabel]]
      fieldTerms <- TERM_FORMS[[fieldLabel]]
      tokenMode <- options[['token_mode']]
      caseSensitive <- !is.null(options[['case_sensitive']]) && options[['case_sensitive']]
      if (!caseSensitive) {
        text <- tolower(text)
        term <- tolower(term)
      }
      terms <- if (is.null(fieldTerms[[term]]))
          list(term) else fieldTerms[[term]]
      firstTerm <- terms[[1]]
      if (tokenMode == TM_FULL_TERM) {
        return(fullTermMatch(text, firstTerm))
      }
      if (tokenMode == TM_ALL && lengths(terms) == 1) {
        if (regexpr(FULL_TERM_PATTERN, firstTerm, perl=TRUE) > 0) {
          # full term match in 'all' token mode
          return(if (text == firstTerm) 1 else 0)
        }
      }
      return(termMatchesTokens(text, terms));
    };

    termMatchesTokens <- function (text, terms) {

      # Computes term matches depending on the chosen text analysis options
      #
      # @param {string} text Input text
      # @param {array} terms String array of terms to match

      terms <- paste(terms, collapse='(\\\\b|_)|(\\\\b|_)')
      pattern <- paste('(\\\\b|_)', terms, '(\\\\b|_)', sep="")
      matches <- gregexpr(pattern, text , perl=TRUE)
      if (matches < 0)
        return(0)
      return(lengths(matches))
    }

"""
        return body

    def r_item_analysis_body(self, item_analysis_predicates):
        """ Writes auxiliary functions to handle the item analysis fields

        """
        item_analysis_options = set(map(lambda x: x[0],
                                        item_analysis_predicates))
        item_analysis_predicates = set(item_analysis_predicates)

        body = u""
        # static content
        body += """
    ITEM_ANALYSIS <- list("""
        lines = []
        for field_id in item_analysis_options:
            inner_lines = []
            field = self.tree.fields[field_id]
            lines.append("""
        \"%s\"=list(""" % field['dotted'])
            for option in field['item_analysis']:
                if option in ITEM_OPTIONS and field['item_analysis'][option] \
                        is not None:
                    value = repr(field['item_analysis'][option])
                    value = value if not value.startswith("u") else value[1:]
                    inner_lines.append("""
                \"%s\"=%s""" % (option, value))
            lines[-1] = lines[-1] +  ",\n".join(inner_lines)
        lines[-1] = lines[-1] + """
        )"""
        body += ",\n".join(lines) + """
    )"""

        body += """
    escape <- function (text) {
      return(gsub("(\\\\W)", "\\\\\\\\\\1", text))
    };


    itemMatches <- function (text, fieldLabel, item) {

      # Computes item matches depending on the chosen item analysis options
      #
      # @param {string} text Input text
      # @param {string} fieldLabel Name of the field
      # @param {string} item Item to compare

      if (is.na(text))
        return(0)
      options <- ITEM_ANALYSIS[[fieldLabel]]
      separator <- options[["separator"]]
      pattern <- options[["separator_regexp"]]
      if (is.null(pattern)) {
        if (is.null(separator)) {
          separator <- " "
        }
        pattern <- escape(separator)
      }
      inputs <- strsplit(text, pattern)
      if (item %in% inputs[[1]])
        return(1)
      return(0)
    }

"""
        return body
