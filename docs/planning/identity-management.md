[Go back to planning home](README.md)
# Identity Management
> This document outlines how the open-health-server manages access and identities

Open-health-server manages identity management in two separate realms: users and persons.

## Types
### Users
Users are accounts that provide visibility to metrics, for one specific person or multiple.
### Persons
Persons are identifiers to tie metrics to a human identity. This allows for the separation of access and ownership. A person can exist without a user account, allowing data to be logged on their behalf by another user.

## Example Scenarios
### One to one access
One user can access one person's metrics. This is the most common use case.
### One to many access
One user can access the metrics of multiple persons. This could be useful for a coach viewing the overall health metrics of their team.
### Many to one access
Many users could access the metrics of a single person. This could be beneficial when multiple sport coaches (working independently) could access the health metrics of one person (the client).
### Proxy access
A user can log data on behalf of a person who has no user account. This is useful for logging data for a child, a patient, or an athlete who does not manage their own account.