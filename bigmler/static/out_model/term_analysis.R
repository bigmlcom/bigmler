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
