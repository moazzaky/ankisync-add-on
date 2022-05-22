# Copyright (C) 2020-2022 Edward Husarcik, MD <https://www.husarcik.com/>
#
# This file is part of AnkiSync add-on, an add-on for the program Anki.
#
# AnkiSync addon is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option)
# any later version.


from aqt import mw

# default card type for front/back, non-cloze with notes
default_card_name = "AnkiSync"

css = """
hr {
opacity: .75;
}
    
.card {
  font-family: arial;
  font-size: 20px;
  text-align: center;
  color: black;
  background-color: #D1CFCE;
}

#front {
    padding-top: 30px;
}

#edit {
    position: absolute;
    top: 0;
    right: 0;
	font-size: 12px;
    margin-top: 10px;
    margin-right: 10px;
    color: blue;
}

#deck {
    display: none;
    position: absolute;
    top: 0;
    left: 0;
	font-size: 10px;
    margin-top: 10px;
    margin-left: 10px;
}

#tags {
    position: absolute;
    bottom: 0;
    right: 0;
	font-size: 10px;
    margin-bottom: 10px;
    margin-right: 10px;
}

#updated-at { 
    position: absolute;
    bottom: 0;
    left: 0;
	font-size: 10px;
    margin-bottom: 10px;
    margin-left: 10px;
}
    
    """

qfmt = """
<div id='updated-at'>Last Updated: {{_updated_at}}</div>

<a id='edit' href='https://ankisync.com/flashcards/{{text:_id}}/suggest'>Suggest Edit</a>

<div id='front'>{{_front}}</div>


<div id='deck'>{{Deck}}</div>

<span id='_updated-at' style='display: none;'>{{_updated_at}}</span>

<script>
var string = document.getElementById('_updated-at').innerHTML,
    date = new Date(string);



document.getElementById('updated-at').innerHTML = 'Last Updated: ' + date.toLocaleString();

</script>
    """

afmt = """
    {{FrontSide}}

<hr>

<div id='tags'>{{Tags}}</div>
{{_back}}
    """


# DEFAULT NOTE TYPE START
def create_default_note_type() -> bool:

    # create note type variable
    m = mw.col.models.new(default_card_name)

    # set css
    m['css'] = css

    # create field variables
    notes_field = mw.col.models.new_field("local_notes")
    extra_field = mw.col.models.new_field("_extra")
    front_field = mw.col.models.new_field("_front")
    back_field = mw.col.models.new_field("_back")
    updated_at_field = mw.col.models.new_field("_updated_at")
    id_field = mw.col.models.new_field("_id")

    # add fields
    mw.col.models.add_field(m, notes_field)
    mw.col.models.add_field(m, extra_field)
    mw.col.models.add_field(m, front_field)
    mw.col.models.add_field(m, back_field)
    mw.col.models.add_field(m, updated_at_field)
    mw.col.models.add_field(m, id_field)

    # add templates, for a basic flashcard use one template
    template = mw.col.models.new_template("Card")
    template["qfmt"] = qfmt
    template["afmt"] = afmt

    mw.col.models.add_template(m, template)

    # save note type
    mw.col.models.save(m)

    # check if saved
    nm = mw.col.models.byName(default_card_name)

    # create if does not exist
    if nm is None:
        return False

    return True


def check_if_default_note_type_exists():
    m = mw.col.models.by_name(default_card_name)

    if m is None:
        return False

    return m

def update_default_note_type():
    m = mw.col.models.by_name(default_card_name)

    if m is None:
        return False

    m['css'] = css

    template = m['tmpls'][0]

    template["qfmt"] = qfmt
    template["afmt"] = afmt

    mw.col.models.save(m)


# checks basic note type; 60506e97ac36e2b22db1daaf4bfcbbb29e74a04f
def validate_default_note_type():
    m = mw.col.models.byName(default_card_name)

    if m is None:
        return False

    # create if does not exist
    # if m is None:
        #create_default_note_type()

    # validate fields
    # field_names = mw.col.models.fieldNames(m)

    # validate templates

    # this interesting function makes a hash of the field ("flds") names and template ("tmpls") names.
    # If they do not match, the compared models probably do not either.
    hash = mw.col.models.scmhash(m)

    return hash == '51785c95e366e5312add2735fe9d1b596595a1ba'


# todo... name has to be unique. likely will do AnkiSync - uuid - version
def create_model(name, fields):
    return

def compare_note_type(m1,m2):
    return False

# validates based upon anki's build in scmhash function and our added type comparison (eg, basic vs cloze)
def validate_model(name, field_names, template_names, type):

    return

