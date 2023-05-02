"""Wrapper for the GPT4All-J model."""
from functools import partial
from typing import Any, Dict, List, Mapping, Optional, Set

from pydantic import Extra, Field, root_validator

from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain.llms.base import LLM
from langchain.llms.utils import enforce_stop_tokens


class GPT4All_J(LLM):
    r"""Wrapper around GPT4All-J language models.

    To use, you should have the ``pygpt4all`` python package installed, the
    pre-trained model file, and the model's config information.

    Example:
        .. code-block:: python

            from langchain.llms import GPT4All_J
            model = GPT4All_J(model="./models/gpt4all-model.bin")

            # Simplest invocation
            response = model("Once upon a time, ")
    """

    model: str
    """Path to the pre-trained GPT4All model file."""

    n_threads: Optional[int] = Field(4, alias="n_threads")
    """Number of threads to use."""

    n_predict: Optional[int] = 256
    """The maximum number of tokens to generate."""

    temp: Optional[float] = 0.8
    """The temperature to use for sampling."""

    top_p: Optional[float] = 0.95
    """The top-p value to use for sampling."""

    top_k: Optional[int] = 40
    """The top-k value to use for sampling."""

    echo: Optional[bool] = False
    """Whether to echo the prompt."""

    stop: Optional[List[str]] = []
    """A list of strings to stop generation when encountered."""

    repeat_last_n: Optional[int] = 64
    "Last n tokens to penalize"

    repeat_penalty: Optional[float] = 1.3
    """The penalty to apply to repeated tokens."""

    n_batch: int = Field(1, alias="n_batch")
    """Batch size for prompt processing."""

    streaming: bool = False
    """Whether to stream the results or not."""

    client: Any = None  #: :meta private:

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the identifying parameters."""
        return {
            "seed": self.seed,
            "n_predict": self.n_predict,
            "n_threads": self.n_threads,
            "n_batch": self.n_batch,
            "repeat_last_n": self.repeat_last_n,
            "repeat_penalty": self.repeat_penalty,
            "top_k": self.top_k,
            "top_p": self.top_p,
            "temp": self.temp,
        }

    @staticmethod
    def _llama_param_names() -> Set[str]:
        """Get the identifying parameters."""
        return {}

    @root_validator()
    def validate_environment(cls, values: Dict) -> Dict:
        """Validate that the python package exists in the environment."""
        try:
            from pygpt4all.models.gpt4all_j import GPT4All_J as GPT4AllModel
            
            llama_keys = cls._llama_param_names()
            model_kwargs = {k: v for k, v in values.items() if k in llama_keys}
            values["client"] = GPT4AllModel(
                model_path=values["model"],
                **model_kwargs,
            )

        except ImportError:
            raise ValueError(
                "Could not import pygpt4all python package. "
                "Please install it with `pip install pygpt4all`."
            )
        return values

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {
            "model": self.model,
            **self._default_params,
            **{
                k: v
                for k, v in self.__dict__.items()
                if k in GPT4All_J._llama_param_names()
            },
        }

    @property
    def _llm_type(self) -> str:
        """Return the type of llm."""
        return "gpt4all"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
    ) -> str:
        r"""Call out to GPT4All's generate method.

        Args:
            prompt: The prompt to pass into the model.
            stop: A list of strings to stop generation when encountered.

        Returns:
            The string generated by the model.

        Example:
            .. code-block:: python

                prompt = "Once upon a time, "
                response = model(prompt, n_predict=55)
        """
        if run_manager:
            text_callback = partial(run_manager.on_llm_new_token, verbose=self.verbose)
            text = self.client.generate(
                prompt,
                new_text_callback=text_callback
            )
        else:
            text = self.client.generate(prompt)
        if stop is not None:
            text = enforce_stop_tokens(text, stop)
        return text