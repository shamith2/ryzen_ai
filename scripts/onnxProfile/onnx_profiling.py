# Script for profiling onnx model

import os
import sys

import onnx
import onnxruntime

from pathlib import Path

from onnxInsights.onnxHelpers import ONNXTransformer

workspace = Path(__file__).parent.resolve()

onnx_t = ONNXTransformer()

uninferred_onnx_model_path = os.path.join(workspace, 'models', 'model.onnx')

def get_shapes(model_path):
    dummy_session = onnxruntime.InferenceSession(
                    model_path,
                    providers=["CPUExecutionProvider"]
                )
    
    print("Inputs: ")
    for _input in dummy_session.get_inputs():
        print(_input.name, _input.shape, _input.type)
    
    print("Outputs: ")
    for output in dummy_session.get_outputs():
        print(output.name, output.shape, output.type)
    
    sys.exit()


# get_shapes(uninferred_onnx_model_path)

# inferred_onnx_model_path = onnx_t.shapeInfer('sdxlt_unet', uninferred_onnx_model_path, [(1, 4, 64, 64), (1,), (1, 77, 2048), (1, 1280), (1, 6)], [(1, 4, 64, 64)])

# for llm: phi 1.5
PHASE = 'PROMPT'
BATCH_SIZE = 1
SEQ_LEN = 2048 if PHASE == 'PROMPT' else 1
MAX_LEN = 4096
CACHE_LEN = 1 if PHASE == 'PROMPT' else MAX_LEN

uninferred_llm_onnx_model_path = os.path.join(workspace, 'models', 'model.onnx')

input_shapes = [(BATCH_SIZE, SEQ_LEN), (1, MAX_LEN), (BATCH_SIZE, SEQ_LEN)]

for i in range(24):
    input_shapes.append((BATCH_SIZE, 32, MAX_LEN - 1, 64)) # for key
    input_shapes.append((BATCH_SIZE, 32, MAX_LEN - 1, 64)) # for value

output_shapes = [(BATCH_SIZE, SEQ_LEN, 51200)]

for i in range(24):
    output_shapes.append((BATCH_SIZE, 32, MAX_LEN, 64)) # for key
    output_shapes.append((BATCH_SIZE, 32, MAX_LEN, 64)) # for value

inferred_onnx_model_path = onnx_t.shapeInfer(
    'phi-1_5',
    uninferred_llm_onnx_model_path,
    input_shapes,
    output_shapes
)

onnx_t.profileMemory(inferred_onnx_model_path)

# onnx_t.profileModel(inferred_onnx_model_path)

# onnx_t.modifyGraph(delete_block=['DequantizeLinear', 'Clip', 'QuantizeLinear'], upper_2_ok=False, only_middle=True)
