import os
import glob
import argparse

def create_input_model_from_gs(gs_filename, input_model_filename="input_model"):
    """ Also outputs the theoretical input if gold_standard is not
    """
    gold_standard_lines = None
    with open(gs_filename, 'r') as f:
        gold_standard_lines = f.readlines()

    input_model_lines = []
    for line in gold_standard_lines:
        if len(line) > 1: # not a blank line
            line = line.split()
            # remove the BIO tag
            line = line[:-1]
            line = '\t'.join(line)
            line += '\n'
        input_model_lines.append(line)

    # write results
    with open(input_model_filename, 'w') as f:
        f.writelines(input_model_lines)


def match_gs_predictions(gs_filename, predictions_filename, output_filename):
    """ Function that match gold standard with predictions and fills the filenames and spans
    """
    gold_standard_lines = None
    predicted_lines = None

    with open(gs_filename, 'r') as f:
        gold_standard_lines = f.readlines()
    with open(predictions_filename, 'r') as f:
        predicted_lines = f.readlines()


    new_predicted_lines = []
    gs_index = 0
    pred_index = 0
    while gs_index < len(gold_standard_lines) and pred_index < len(predicted_lines):
        gs_line = gold_standard_lines[gs_index]
        pred_line = predicted_lines[pred_index]
        # Not lines with only \n.
        if len(gs_line) > 1 and len(pred_line) > 1:

            # get the token text
            gs_line = gs_line.split()
            pred_line = pred_line.split()

            # if both have the same token
            if gs_line[0] == pred_line[0]:
                # merge filename and spans from gs_line to pred_line
                pred_line[1:4] = gs_line[1:3] + pred_line[-1:]
                new_predicted_lines.append('\t'.join(pred_line) + '\n')
#                 print(gs_index, gs_line, pred_index, pred_line)
                pred_index += 1
                gs_index += 1
            elif gs_line[0] == pred_line[0][:len(gs_line[0])]: # gs_line is inside pred_line
#                 print("gs_line inside pred_line:", gs_index, gs_line, pred_index, pred_line)
                start = 0 # relative index of the start of the gs_line[0] inside pred_line[0] 
                span1 = None
                span2 = None
                while len(gs_line) == 0 or gs_line[0] == pred_line[0][start:start+len(gs_line[0])]:
                    if len(gs_line) > 0:
                        # DONE
                        gs_filename = gs_line[1]
                        gs_span1, gs_span2 = gs_line[2].split('_')
                        if gs_line[0] == pred_line[0][0:len(gs_line[0])]: # gs token is the begining of predicted token
                            span1 = gs_span1
#                         print("gs_line[0]:", gs_line[0], "pred_line[0][start:]:", pred_line[0][start:])
                        if gs_line[0] == pred_line[0][start:]: # gs_token is the end of the predicted token
                            span2 = gs_span2
                            # write new pred token
                            new_pred_token = [pred_line[0], gs_filename, '_'.join([span1, span2]), pred_line[-1]] # assuming all gs filenames were the same in all subtokens
                            new_predicted_lines.append('\t'.join(new_pred_token) + '\n')
#                             print(gs_index, pred_index, "New token:", new_pred_token, "appended")
                        start += len(gs_line[0])
                    gs_index += 1
                    if gs_index < len(gold_standard_lines):
                        gs_line = gold_standard_lines[gs_index]
                        gs_line = gs_line.split()
#                         if len(gs_line) > 0:
#                             print("gs_line inside pred_line WHILE:", gs_index, gs_line[0], pred_index, pred_line[0][start:start+len(gs_line[0])])
#                         else:
#                             print("gs_line inside pred_line WHILE:", gs_index, gs_line, pred_index, pred_line)
                    else:
                        break

                pred_index += 1
            elif pred_line[0] == gs_line[0][:len(pred_line[0])]: # pred_line is inside gs_line
#                 print("pred_line is inside gs_line", pred_index, pred_line, gs_index, gs_line)
                start = 0
                span1 = None
                has_started = False
                while len(pred_line) == 0 or pred_line[0] == gs_line[0][start:start+len(pred_line[0])]:
                    if len(pred_line) > 0:
                        # DONE
                        gs_filename = gs_line[1]
                        gs_span1, gs_span2 = gs_line[2].split('_')
                        if not has_started and pred_line[0] == gs_line[0][0:len(pred_line[0])]: # predicted token is the begining of gs token
                            has_started = True
                            span1 = gs_span1
                        span2 = str(int(span1) + len(pred_line[0]))
                        new_pred_token = [pred_line[0], gs_filename, '_'.join([span1, span2]), pred_line[-1]]
                        new_predicted_lines.append('\t'.join(new_pred_token) + '\n')
#                         print(gs_index, pred_index, "New token:", new_pred_token, "appended")
                        span1 = span2
                        start += len(pred_line[0])
                    else:
                        new_predicted_lines.append('\n')

                    pred_index += 1
                    if pred_index < len(predicted_lines):
                        pred_line = predicted_lines[pred_index]
                        pred_line = pred_line.split()
#                         if len(pred_line) > 0:
#                             print("pred_line is inside gs_line WHILE:", pred_index, pred_line[0], gs_index, gs_line[0][start:start+len(pred_line[0])])
#                         else:
#                             print("pred_line is inside gs_line WHILE:", pred_index, pred_line, gs_index, gs_line)
                    else:
                        break
                gs_index += 1
            else: # Not one inside the other -> advance 
#                 print("ERROR:",  gs_index, gs_line, pred_index, pred_line)
#                 raise NotImplementedError
                print("WARNING: assuming predicted lines were truncated")
                gs_index += 1

            # advance the gold standard
        elif gs_line == pred_line: # if both are new_lines
            new_predicted_lines.append('\n')
            gs_index += 1
            pred_index += 1
        else: # one of both is a new_line
            if len(gs_line) > 1: # if gold_standard has some text move the pred_index 
                new_predicted_lines.append('\n')
                pred_index += 1
            else: # reverse
                gs_index += 1


    # write results
    with open(output_filename, 'w') as f:
        f.writelines(new_predicted_lines)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-gs", "--original_conll", type=str, \
            help="file in conll, containing the filenames and the spans (gold standard)")
    parser.add_argument("-p", "--predictions_in_conll", type=str, \
            help="file in conll, with the predictions (without filenames and spans).")
    parser.add_argument("-o", "--output_predictions_in_conll", type=str, \
            help="output with the predicted conll with the filepaths and spans")

    args = parser.parse_args()

    conll_with_filenames = args.original_conll
    predictions = args.predictions_in_conll
    output_predictions_in_conll = args.output_predictions_in_conll

    create_input_model_from_gs(conll_with_filenames)
    match_gs_predictions(conll_with_filenames, predictions, output_predictions_in_conll)


