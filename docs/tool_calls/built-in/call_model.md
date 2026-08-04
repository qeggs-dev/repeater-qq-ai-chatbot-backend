# Call Model

调用模型接口

注册名：`call_model`

接受参数:
``` json
{
  "model_id": "", // Unique identifier used to locate and load the target model.
  "user_name": "", // Name of the user making the request, used for logging and personalization.
  "temperature": 1.0, // Controls randomness in output. Lower values (e.g., 0.2) make output more deterministic; higher values (e.g., 1.5) increase diversity. Must be between 0 and 2.
  "top_p": 1.0, // Nucleus sampling threshold. The model considers only the smallest set of tokens whose cumulative probability >= top_p. Must be between 0 and 1.
  "presence_penalty": 0.0, // Penalizes tokens that have appeared at all in the text so far, encouraging the model to talk about new topics. Positive values discourage repetition. Range: -2.0 to 2.0.
  "frequency_penalty": 0.0, // Penalizes tokens proportionally to how often they have appeared, reducing verbatim repetition. Positive values discourage frequent tokens. Range: -2.0 to 2.0.
  "max_tokens": 4096, // The maximum number of tokens the model can generate in the response.
  "max_completion_tokens": 4096, // Alias for max_tokens. The maximum number of tokens allowed in the completion output.
  "thinking": null, // When enabled, the model allocates tokens for internal reasoning before producing the final answer. Useful for complex, multi-step problems.
  "stop": null, // List of strings where the model stops generating further tokens when encountered.
  "context": null, // Predefined conversation history or system context to guide the model's behavior.
  "reasoning_effort": null, // Controls how many tokens the model spends on internal reasoning (e.g., 'low', 'medium', 'high').
  "remove_reasoning_prompt": null, // If True, strips the internal reasoning prompt from the output, returning only the final answer.
  "output_role": "assistant", // Role assigned to the generated content in the conversation structure (e.g., 'assistant').
  "timeout": null, // Maximum time in seconds to wait for a response before the request is cancelled.
  "output_format": "text", // Format of the output data returned by the API (e.g., 'text').
  "extra_bodys": {} // Additional parameters to pass to the API call.
}
```

返回模型的输出内容：
``` json
{
  "context": [...] // Model's generated context.
}
```