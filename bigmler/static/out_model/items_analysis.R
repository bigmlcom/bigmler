
    escape <- function (text) {
      return(gsub("(\\W)", "\\\\\1", text))
    }

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

    # predict function
