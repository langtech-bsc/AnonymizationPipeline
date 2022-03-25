from __future__ import annotations
from functools import reduce
from typing import List, TypedDict
from meta import Span

class metric(TypedDict):
    num_entities : int
    strict : int
    exact : int
    partial : int
    soft_partial : int
    chars_total : int
    chars_hidden : int


def compute_metric(original : List[Span], predicted : List[Span]) -> metric:
    original_sorted = sorted(original, key=lambda s: (s['start'], s['end']))
    predicted_sorted = sorted(predicted, key=lambda s: (s['start'], s['end']))
    original_mereged = merge_spans(original_sorted)
    predicted_merged = merge_spans(predicted_sorted)
    

    index_original : int = 0
    index_predicted : int = 0
    chars_total : int = sum([s['end'] - s['start'] for s in original_mereged])
    chars_hidden : int = 0
    exact : int = 0
    strict : int = 0
    soft_partial : int = 0
    partial : int = 0


    while (index_original < len(original_mereged) and index_predicted < len(predicted_merged)):
        span_o : Span = original_mereged[index_original]
        span_p : Span = predicted_merged[index_predicted]
        inter = intersection(span_o, span_p)
        if inter > 0:
            soft_partial += 1
            chars_hidden += inter
            if inter == span_o['end'] - span_o['start']:
                exact += 1
                if span_o['label'] == span_p['label']:
                    strict += 1
                    partial += 1
            else :
                if span_o['label'] == span_p['label']:
                    partial += 1
        if span_o['end'] < span_p['end']:
            index_original += 1
        else:
            index_predicted += 1

    return metric(num_entities=len(original_mereged), strict=strict, exact=exact, partial=partial, soft_partial=soft_partial, chars_total=chars_total, chars_hidden=chars_hidden)

def aggregate_metric(metricA : metric, metricB : metric) -> metric:
    num_entities = metricA['num_entities'] + metricB['num_entities']
    strict = metricA['strict'] + metricB['strict']
    exact = metricA['exact'] + metricB['exact']
    partial = metricA['partial'] + metricB['partial']
    soft_partial = metricA['soft_partial'] + metricB['soft_partial']
    chars_total = metricA['chars_total'] + metricB['chars_total']
    chars_hidden  = metricA['chars_hidden'] + metricB['chars_hidden']
    return metric(num_entities=num_entities, strict=strict, exact=exact, partial=partial, soft_partial=soft_partial, chars_total=chars_total, chars_hidden=chars_hidden)


def intersection(spanA : Span, spanB : Span) -> int:
    if spanB['start'] > spanA['end'] or spanA['start'] > spanB['end']:
        return 0
    else:
        Os = max(spanA['start'], spanB['start'])
        Oe = min(spanA['end'], spanB['end'])

        return Oe - Os

def merge_spans(spans : List[Span]) -> List[Span]:
    if len(spans) == 0:
        return spans
    merged : List[Span] = []
    current_Span = spans[0]
    for span in spans:
        if current_Span['label'] == span['label'] and span['start'] - current_Span['end'] < 2:
            current_Span['end'] = span['end']
        else:
            merged.append(current_Span)
            current_Span = span
    
    merged.append(current_Span)
    
    return merged