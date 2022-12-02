# IANizer: A simple daily task manager app

## Lore

*A friend described a simple app they wanted for themselves, and the IANizer was born as joke/toy app in their honor, for their usage.*

**I wrote this in 1:55:31, and I don't know what may break.**

## Description

This is a simple daily task manager app. It allows you to add or edit tasks along with metadata, expected hours to complete, and due date. Then, it prepares your daily schedule for the maximum hours you want (currently hard-coded to 3 hours), and displays the tasks in order of due-date.

Given a vector of due dates, say $\vec{d}$, and a corresponding vector of expected hours, say $\vec{h}$, the algorithm computes today's hour allocation, $\vec{\mathcal{h}}$ as follows:

$$\mathcal{h}_i = \frac{\frac{h_i}{d_i}}{\sum_{j=1}^N \frac{h_j}{d_j}}$$

where $N$ is the number of tasks.

At the end of every day, before another request is made, the expected hours are updated by subtracting the hours spent on the task from the expected hours.

### What's next?

Someone could clean this up into a legitimate app, there's a whole bunch of low-hanging fruit that might make this quite generally usable:

- [ ] Add a database, replacing the single CSV that hosts data for one user
- [ ] Add a login system, so that multiple users can use the app
- [ ] Add a form to change the number of hours you want to work each day
- [ ] Allow users to review the updation of `My Tasks`, in the likely event that they did not complete the last day's tasks
- [ ] Deploy to a server, so that it can be used by anyone


## Installation

### Local Server

You could throw this on a local server pretty easily and keep it running:

1. Clone the repository
2. Install the requirements as in `conda_env.yml`. You can do this by running `conda env create -f conda_env.yml` in the root directory of the repository.
3. Run `python app.py` in the root directory of the repository.