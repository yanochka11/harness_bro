# Additional Resources

These skills cover specific pieces of the eval process: finding failures, measuring them, and building review tools. Evals as a whole are broader and more human-driven. If you're wondering *why* binary pass/fail instead of Likert scales, why error analysis before metrics, or why code-based checks before LLM judges, these resources explain the reasoning.

## The Course

The [AI Evals for Engineers](https://maven.com/parlance-labs/evals?promoCode=evals-info-url) course by Hamel Husain and Shreya Shankar covers the full process: collecting data, analyzing errors, building evaluators (code-based and LLM-as-Judge), evaluating RAG and agents, wiring evals into CI/CD, and building review interfaces. Designed for engineers and PMs who ship AI products.

## Free Resources

### Reading

- **[LLM Evals FAQ](https://hamel.dev/blog/posts/evals-faq/)**. Practical answers to common eval questions: how to do error analysis, design evaluators, build annotation tools, and use eval insights to debug AI systems.

- **[Creating an LLM Judge That Drives Business Results](https://hamel.dev/blog/posts/llm-judge/)**. How to build LLM-based evaluators through "critique shadowing" with domain experts. Covers binary pass/fail judgments, few-shot prompt design, and iterative calibration.

- **[A Field Guide to Improving AI Products](https://hamel.dev/blog/posts/field-guide/)**. Six practices that separate successful AI teams from struggling ones: error analysis, custom data viewers, domain expert involvement, synthetic data, trustworthy evaluations, and experiment-driven roadmaps.

- **[Your AI Product Needs Evals](https://hamel.dev/blog/posts/evals/index.html)**. A framework for eval systems at three levels: unit tests with assertions, human and model-based evaluation with tracing, and A/B testing. Demonstrated through a real estate AI case study.

- **[Who Validates the Validators?](https://arxiv.org/abs/2404.12272)** (Shreya Shankar et al.). Why error analysis must come before writing evaluators: users need evaluation criteria to grade outputs, but grading outputs helps users define criteria.

### Video

- **[Intro to AI Evals with Lenny Rachitsky](https://youtu.be/BsWxPI9UM4c)**. Hamel and Shreya walk through the eval process end-to-end: start with manual error analysis, categorize failure modes, then build targeted evaluators that drive a continuous improvement loop.
