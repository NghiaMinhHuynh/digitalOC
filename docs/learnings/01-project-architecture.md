# What I Learned: Project Architecture

DigitalOC helped me understand how a full-stack machine learning project needs clear boundaries between the user interface, the API, the data pipeline, and the trained model artifacts. The project is not just a React app or just a set of Python scripts. It only works when each layer passes the right information to the next one.

The biggest architectural lesson I learned is that the structure of the project affects how easy it is for the team to build, test, explain, and improve the product. DigitalOC has several major parts: the React frontend, the Flask backend, the data collection and cleaning scripts, the model training scripts, saved model artifacts, and planning documents. Each part has a different responsibility, but all of them depend on each other.

At first, it can be tempting to think of a project like this as a list of features. For example, the app needs a home page, a situation input page, a result page, and model predictions. After working with the codebase, I learned that the more important question is how those features connect. The frontend needs to know what information to ask the user for. The backend needs to know how to receive that information. The model needs the information in the same format it saw during training. The result page needs the model output to be readable enough for a user to trust it.

## Main Takeaways

- A frontend should collect user intent in a predictable format before sending it to the backend.
- A Flask API can act as the bridge between user inputs and machine learning predictions.
- Model files, data files, and training scripts need predictable locations so the app can be run and debugged by other team members.
- Documentation matters because full-stack projects have more setup steps than single-file assignments.
- Folder organization is not just cosmetic. It communicates how the project is supposed to be understood.
- A working feature is easier to maintain when each layer has one clear job.
- Integration points, such as API requests and model input features, need extra attention because small mismatches can break the whole flow.

## What I Noticed in DigitalOC

DigitalOC separates most of the frontend code into a `frontend` folder and most of the backend work into a `backend` folder. This is helpful because it makes the project easier to navigate. The frontend includes pages, components, styling, and image assets. The backend includes data files, scripts for getting and processing data, model training files, model artifacts, and the Flask application.

This separation taught me that a full-stack project should make it obvious where different kinds of work belong. If someone is changing how the user enters a game situation, they probably need to look at the React pages and components. If someone is changing how the recommendation is calculated, they probably need to look at the Flask route and the model scripts. If someone is changing the data used by the models, they need to understand the data processing scripts.

I also learned that architecture affects teamwork. When folders and responsibilities are clear, teammates can work at the same time without constantly stepping on each other's code. For example, one person can improve the result page while another person improves the backend response, as long as they agree on the data shape between them.

## Challenges I Learned From

One challenge with this type of project is that the frontend and backend can both be correct by themselves but still fail together. For example, the frontend might send a value under one name while the backend expects a different name. The backend might return a prediction in a format that is technically valid but difficult for the frontend to display. This helped me understand why API contracts are important.

Another challenge is that machine learning projects often create extra files, such as model artifacts, processed datasets, and cache files. I learned that a team needs to decide which files belong in the repository and which files should be regenerated locally. Without that decision, the project can become harder to clone, slower to review, and more confusing for new contributors.

## Why This Matters

Before working on this project, it was easy to think about the frontend and backend as separate pieces. DigitalOC made it clearer that the architecture is the product. A good play recommendation depends on the frontend collecting the correct game situation, the backend validating and transforming those values, and the models returning outputs in a form the UI can explain.

Good architecture also makes the project easier to explain to someone else. If a project lead or teammate asks how DigitalOC works, I can now describe the flow from user input to recommendation: the user enters a game situation, the frontend sends the data to the backend, the backend prepares the features, the model makes predictions, and the frontend displays the result. That explanation is much clearer than saying the project "uses React, Flask, and machine learning."

This matters because real software projects are rarely just about writing code that works one time. They need to be understandable, reusable, and organized enough for future changes. If the team wants to add defensive formations, support more seasons of data, or improve the play drawing feature, the architecture should make those changes possible without rewriting everything.

## How I Can Apply This Later

In future projects, I would start by sketching the data flow between pages, API routes, model inputs, and model outputs before writing too much code. That would make it easier to divide team responsibilities and catch integration problems earlier.

I would also create documentation earlier in the project. Even a simple architecture note can save time later because it gives the team a shared understanding of the system. For future full-stack projects, I would document the main folders, the purpose of each major file, the route between frontend and backend, and the expected format of important data.

Another habit I want to build is checking whether new code belongs in the right layer. If logic is only about display, it probably belongs in the frontend. If logic is about preparing model inputs or protecting the model from invalid values, it probably belongs in the backend. If logic is about building the dataset, it probably belongs in the data pipeline. Thinking this way would help me write cleaner code and make better decisions as a teammate.
