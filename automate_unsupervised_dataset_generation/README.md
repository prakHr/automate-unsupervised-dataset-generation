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
results = automate_unsupervised_dataset_generation.automate.parallel_scraping(query,num_page)

query = ["Artificial Intelligence","Cake"]
num_page = 1
rv = automate_unsupervised_dataset_generation.automate.scale_parallel_scraping(query,num_page)
pprint(rv)
```

## License

`automate-unsupervised-dataset-generation` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
