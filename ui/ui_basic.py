import sys

def simulation(tweet):
    return "simulation"

def expected_value(tweet):
    return "expected_value"

def max_expected_value():
    return "maximize_probility_reach_node"

def maximize_probility_reach_node(person, tweet=None):
    if tweet == None:
        return "maximize_probility_reach_node(person, tweet=None)"
    else:
        return "maximize_probility_reach_node(person, tweet)"


if __name__ == "__main__":
    s = ""
    while "esc" not in s:
        print "premi"

        print "1-[SIMULAZIONE] Cosa POTREBBE SUCCEDERE dato un certo tweet coi relativi hashtags"
        print "2-[VALORE ATTESO] Avere il valore atteso dato un certo tweet coi relativi hashtags"
        print "3-[MASSIMIZZARE IL VALORE ATTESO] (consiglia gli hashtag da usare per massimizzare il risultato(cioe la visibilita della SOURCE)"
        print "4-[MASSIMIZZARE LA PROBABILITA' DI RAGGIUNGERE UN CERTO NODO]dato un certo tweet coi relativi hashtags" \
              " e la peronsa da raggiungere, o solo la persona."
        s = sys.stdin.readline()

        if "1" in s or "2" in s:
            print "inserisci un tweet coi relativi hashtag"
            tweet = sys.stdin.readline()
            # print "tweet: ", tweet

        if "1" in s:
            # [SIMULAZIONE]
            print "[SIMULAZIONE]"
            print simulation(tweet)
        elif "2" in s:
            # [VALORE ATTESO]
            print "[VALORE ATTESO]"
            print expected_value(tweet)

        elif "3" in s:
            # [MASSIMIZZARE IL VALORE ATTESO]
            print "[MASSIMIZZARE IL VALORE ATTESO]"
            print max_expected_value()

        elif "4" in s:
            # [MASSIMIZZARE LA PROBABILITA' DI RAGGIUNGERE UN CERTO NODO]
            print "[MASSIMIZZARE LA PROBABILITA' DI RAGGIUNGERE UN CERTO NODO]"

            print "premi"
            print "     a- inserisci solo la persona"
            print "     b- inserisci solo la persona, il tweet e gli hashtag da inserire"
            choose = sys.stdin.readline()

            if "a" in choose:
                print "inserisci la persona: "
                person = sys.stdin.readline()
                print maximize_probility_reach_node(person)
            elif "b" in choose:
                print "inserisci la persona: "
                person = sys.stdin.readline()
                print "inserisci il tweet con gli hashtag: "
                tweet = sys.stdin.readline()
                print maximize_probility_reach_node(person, tweet)


            else:
                print "digita solo 'a' o 'b'"

        else:
            print "digita solo 1,2,3 o 4"


        print "--------------------------------------------------"