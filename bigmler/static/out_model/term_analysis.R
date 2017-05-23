
    FULL_TERM_PATTERN <- '^.+\\b.+$'

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
      return(termMatchesTokens(text, terms))
    }

    termMatchesTokens <- function (text, terms) {

      # Computes term matches depending on the chosen text analysis options
      #
      # @param {string} text Input text
      # @param {array} terms String array of terms to match

      terms <- paste(terms, collapse='(\\b|_)|(\\b|_)')
      pattern <- paste('(\\b|_)', terms, '(\\b|_)', sep="")
      matches <- gregexpr(pattern, text , perl=TRUE)
      if (matches < 0)
        return(0)
      return(lengths(matches))
    }
