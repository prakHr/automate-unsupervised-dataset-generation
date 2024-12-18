# automate-unsupervised-dataset-generation
-----

## Table of Contents

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install automate-unsupervised-dataset-generation
```

## Start the app
```
import automate_unsupervised_dataset_generation.automate
query = "Artificial Intelligence"
num_page = 5
sleep_time = 10
results = automate_unsupervised_dataset_generation.automate.parallel_scraping(query,num_page,sleep_time)
```

## License

`automate-unsupervised-dataset-generation` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
