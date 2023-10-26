Rotate Authorship
^^^^^^^^^^^^^^^^^

The METplus team rotates the list of authors in the citation instructions
for each official release:

* Compare the current |projectRepo| User's Guide citation to the most recent
  official release.

* If needed, update the authorship order, moving the previous first author to
  the end of the list. Note the format difference in the first name in the
  citation list compared with the others.  The first name in the citation list
  is "Last name, First Initial." and all of the following names as
  "First Initial. Last Name".  Please maintain that format as it is the most
  common format for citations.

* The author list is typically found in the conf.py file in the documentation
  directory, i.e. *docs/conf.py*.
  Most of the component repositories store the list of authors in a variable
  named **author_list**. Please ensure that changes to this list match the
  correct format listed above.
  In the METplus repository, the conf.py file has variable named
  CURRENT_AUTHORS that is a list of the authors to rotate.
  To rotate, move the first item in the list to the end of the list.
  There is logic in this file to read the list and format it properly to match
  the expected format for citations.

* Review the list of authors in the citation and at the top level of the
  documentation and update as needed.
  
* Commit changes and push to GitHub
