import random


def start_quiz(nb_questions=5, tables=[]):
    x = random.randint(0, 12)
    y = random.randint(0, 12)

    if tables:
        tables = map(int, tables)
        y = tables[random.randint(0, len(tables) - 1)]

    session_state = {
        "x": x,
        "y": y,
        "good": 0,
        "bad": 0,
        "step": 0,
        "tables": tables,
        "nb_questions": nb_questions
    }

    return session_state, _create_question(x, y, "")


def check_user_answer(session_state, answer):
    if session_state is None:
        print "Error: session_state est Vide ==> intent démarré hors session de dialogue"
        return session_state, "", False

    # We just try keep listening to the user until we get an answer
    if answer is None:
        return session_state, "", True

    correction_sentence = _generate_correction(session_state, answer)

    next_step = _create_next_step(correction_sentence, session_state)

    return next_step["session_state"], next_step["sentence"], next_step["continues"]


def user_does_not_know(session_id, sessions_states):
    if session_id is None or sessions_states.get(session_id) is None:
        print "[Alerte] Pas de jeu dans cette session"
        raise ValueError('[ERREUR] Une session doit etre associé avec l ail dit de cette session.')
    session_state = sessions_states.get(session_id)
    answer = session_state["x"] * session_state["y"]

    next_step = _create_next_step("Pas d'inquiétude, la bonne réponse était " + str(answer), session_state)

    return next_step["sentence"], next_step["continues"]


def terminate_early(sessions_states, session_id):
    remove_session_state(sessions_states, session_id)
    return "Comme demandé le jeu est terminé"


def _create_next_step(sentence, session_state):
    session_state["step"] += 1

    if session_state.get("step") < session_state.get("nb_questions"):
        session_state["x"] = random.randint(0, 11)
        session_state["y"] = random.randint(0, 11)

        if session_state.get("tables"):
            tables = session_state["tables"]
            session_state["y"] = tables[random.randint(0, len(tables) - 1)]

        sentence = _create_question(session_state["x"], session_state["y"], sentence)
        continues = True
    else:
        sentence += " Vous avez " + str(session_state["good"]) + " bonne réponses et " + str(
            session_state["bad"]) + " mauvaises réponses "
        sentence = _create_end_sentence(sentence)
        session_state = {}
        continues = False

    return dict(sentence=sentence, continues=continues, session_state=session_state)


def save_session_state(sessions_states, session_id, new_state):
    sessions_states[session_id] = _set_not_none_dict_value(sessions_states.get(session_id), new_state)


def remove_session_state(sessions_states, session_id):
    sessions_states[session_id] = None


def _generate_correction(session_state, user_answer):
    x = session_state["x"]
    y = session_state["y"]

    if x is None or y is None:
        raise ValueError("Il manque une information pour la question posée")

    if user_answer is None:
        return ""

    result = x * y

    if result == user_answer:
        sentence = "C'est tout. Bien joué."
        session_state["good"] += 1
    elif result != user_answer:
        sentence = "Mauvaise réponse. {} fois {} est égal à  {}".format(x, y, result)
        session_state["bad"] += 1

    return sentence


def _set_not_none_dict_value(to_update, update):
    to_update = to_update or {}
    for key, value in update.iteritems():
        if value is not None:
            to_update[key] = value
    return to_update


def _create_end_sentence(sentence):
    return sentence + " Le jeu est terminé "


def _create_question(x, y, intro_sentence=""):
    question = "Combien font  {} fois {} ?".format(x, y)
    return intro_sentence + " " + question
