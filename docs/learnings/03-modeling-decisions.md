# What I Learned: Modeling Decisions

DigitalOC helped me learn that model selection is only one part of building a prediction system. The more important question is whether the model output matches the decision the product needs to make. For this project, the app needs to recommend offensive play choices and explain expected outcomes in a way that makes sense for football.

Before this project, I mostly thought about machine learning in terms of choosing an algorithm and training it on data. DigitalOC helped me see that the modeling process starts earlier than that. The team first has to decide what problem the model is solving. In this case, the product is not only trying to predict what teams usually do. It is trying to help recommend an offensive decision for a specific game situation.

That difference matters. A model that predicts the most common play call is not always the same as a model that recommends the best play call. If teams usually run in a certain situation, that does not automatically mean running is the best choice. This helped me understand that model outputs need to be interpreted carefully and connected to the purpose of the app.

## Main Takeaways

- Classification models are useful for choosing between categories like run and pass.
- Regression-style outputs are useful for estimating results like expected yards, EPA, or success probability.
- Models need metadata because the app must know how to encode inputs and interpret outputs.
- A model can be technically correct but still hard to use if its output is not connected to the user experience.
- The prediction target should match the product goal.
- Model performance should be measured in a way that reflects the decision being made.
- Feature choices affect what the model can and cannot learn.
- The model output should be understandable enough for the frontend to explain.

## What I Noticed in DigitalOC

DigitalOC uses different kinds of models for different questions. One model can help classify a situation as more favorable for a run or pass. Other models can estimate expected outcomes for run or pass plays. This taught me that one model does not have to solve the entire problem. A larger prediction system can combine several smaller models, each with a specific responsibility.

The project also uses football-specific features, such as down, yards to go, field position, score differential, time remaining, timeouts, and team strength. These features make sense because they are the same kinds of information coaches and fans use when thinking about play calling. This helped me understand that feature selection should be connected to the real-world decision.

Another important lesson is that model artifacts need supporting metadata. A saved model file alone is not always enough. The app also needs to know which features the model expects, how categorical values were encoded, and how to interpret the output. Without that information, it becomes much harder to use the model safely in a backend application.

## Challenges I Learned From

One challenge is deciding what "success" means. In football, success could mean gaining enough yards, increasing expected points, avoiding turnovers, improving win probability, or setting up the next down. Different definitions can lead to different model behavior. This taught me that the target variable is a design decision, not just a column in a dataset.

Another challenge is separating prediction from recommendation. A model might predict that a pass has a higher expected gain, but the app still has to decide how to communicate that to the user. It may need to compare multiple values, such as expected yards, success probability, and risk. This means the product logic around the model can be just as important as the model itself.

I also learned that models can be limited by their training data. If the training data only includes certain seasons, teams, or play types, the model may not generalize perfectly to every situation. This does not make the model useless, but it means the app should be careful about how confident it sounds.

## Why This Matters

Sports predictions are not just about accuracy. They also need to support decisions. A coach-facing or fan-facing tool needs outputs that are readable, comparable, and tied to the actual game situation. That means the model pipeline should be designed with the final recommendation screen in mind.

This matters because users do not interact with a model directly. They interact with the explanation, the numbers, and the recommendation shown by the app. If the output is confusing, users may not know whether to trust it. If the output is too simple, it may hide important uncertainty. DigitalOC helped me see that machine learning should be treated as part of the user experience, not just a backend feature.

Modeling decisions also matter for team communication. If everyone understands the target variable, input features, and evaluation approach, it is easier to discuss improvements. If those choices are not documented, teammates may accidentally compare models that are solving different problems.

## How I Can Apply This Later

In future projects, I would define the product question before choosing the model. Instead of starting with "which algorithm should we use," I would ask "what decision should the user be able to make from this output?"

I would also write down the model target, features, assumptions, and limitations. This would make the project easier to explain and easier to improve later. For example, if a future version of DigitalOC uses more seasons of data or adds defensive information, the team could compare the new model against the old one more clearly.

Another lesson I will apply is to think about the model response format early. The frontend needs outputs that can become readable text, charts, or comparisons. If the model only returns raw numbers without context, the user experience becomes harder to build. In future projects, I would design model outputs with both accuracy and presentation in mind.
