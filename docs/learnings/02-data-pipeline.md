# What I Learned: Data Pipeline

DigitalOC showed me that machine learning results depend heavily on the quality and consistency of the data pipeline. The project combines play-by-play data, participation data, Next Gen Stats, snap counts, and team ratings. Each data source adds useful context, but it also adds more chances for missing values, mismatched columns, or inconsistent naming.

The data pipeline is one of the most important parts of the project because it decides what the models are actually learning from. Before working on DigitalOC, I thought of data cleaning as something that happens before model training. This project helped me understand that data cleaning, feature engineering, and model design are connected. If the dataset does not represent football situations correctly, then the model cannot make strong recommendations no matter which algorithm is used.

DigitalOC uses football data from multiple areas of the game. Play-by-play data describes the situation and result of individual plays. Next Gen Stats adds more detail about passing, rushing, and receiving performance. Snap count and participation data can help explain which players were involved. Team Elo ratings add a way to represent team strength. These sources are useful together because football decisions are situational. A run or pass recommendation depends on down, distance, field position, score, time, team strength, and sometimes personnel.

## Main Takeaways

- Cleaning data is part of model design, not just preparation before the "real" work.
- Feature names and formats need to stay consistent between training scripts and the Flask app.
- Sports data often needs domain-specific interpretation, such as down, distance, field position, personnel, time remaining, and score differential.
- Saving processed datasets can make model training faster and easier to reproduce.
- Combining multiple datasets requires careful handling of keys such as team names, seasons, weeks, game IDs, and play IDs.
- Missing values should be handled intentionally because filling them incorrectly can change what the model learns.
- Feature engineering is where domain knowledge becomes part of the machine learning system.
- Reproducibility matters because teammates should be able to regenerate the same training data from the same raw sources.

## What I Noticed in DigitalOC

DigitalOC has scripts for gathering data, merging data, calculating success, adding participation features, and training models. Seeing those files helped me understand that a machine learning app is not only the final model file. The model is the end result of a chain of choices.

One important choice is deciding which columns should become model features. In football, raw data often needs to be transformed into more useful values. For example, a model might need score differential instead of separate home and away scores. It might need a field position number instead of a text description. It might need time remaining in a consistent format. These transformations make the data easier for the model to learn from.

Another important choice is deciding how to merge datasets. Football datasets can describe the same event in different ways. If two files use different team abbreviations or if one file has missing plays, the merged dataset can become inaccurate. I learned that checking merge results is just as important as writing the merge code. A merge that runs without errors can still be wrong if it drops rows or duplicates plays unexpectedly.

## Challenges I Learned From

One challenge is that sports data contains a lot of edge cases. Plays can be penalties, kneel downs, spikes, sacks, scrambles, no plays, or special situations. Some of those should be included in a model, and others might need to be filtered out depending on the prediction goal. This taught me that data cleaning requires understanding the subject, not just programming.

Another challenge is keeping training features aligned with prediction features. The model is trained using a certain set of columns. Later, the Flask app has to create those same columns from user input. If the backend sends the model a different feature order, a missing column, or a different encoding, the prediction may be unreliable. This made me realize why metadata files and consistent preprocessing steps are so important.

I also learned that storing processed datasets can help development move faster. If the team has to download and clean all raw data every time, training becomes slower and more frustrating. However, processed files should still be documented so people understand where they came from and how to recreate them.

## Why This Matters

The models can only make useful recommendations if the data describes the football situation accurately. A small mismatch, such as using a team abbreviation inconsistently or passing a field position value in the wrong range, can make the output less reliable even if the model code runs without errors.

This matters even more in a project like DigitalOC because users may trust the recommendation if the app looks polished. A good interface can make a bad prediction seem more official than it really is. That means the data pipeline has a responsibility to support accurate and honest outputs. If the data is incomplete or inconsistent, the model result should be treated carefully.

The data pipeline also matters for teamwork. If one teammate changes a column name in a processed dataset, another teammate's model script or backend route might break. If the transformations are documented, those changes are easier to understand and fix. Without documentation, people have to guess why a feature exists or where it came from.

## How I Can Apply This Later

For future machine learning projects, I would document each dataset, the columns used from it, and the transformations applied before training. That would help teammates understand where each model feature comes from and make debugging much faster.

I would also add more checks while building datasets. For example, I would check how many rows exist before and after merges, how many missing values are in important columns, and whether categorical values like team abbreviations are consistent. These checks would make the data pipeline more trustworthy.

Another thing I would do in the future is write a short data dictionary. It does not have to be complicated, but it should explain the important fields, what they mean, and how they are used by the model. That would make the project easier to present and easier for a new teammate to join.
