"""
Permission and access control simulation for document retrieval.
"""
from __future__ import annotations

def filter_accessible_documents(
    document_ids: list[str],
    user_permissions: list[str],
    document_acl: dict[str, list[str]]
) -> list[str]:
    """
    Filters a list of document IDs, retaining only those that the user has permission to access.
    
    :param document_ids: List of document IDs to filter.
    :param user_permissions: List of permissions/roles the user possesses.
    :param document_acl: A mapping from document ID to a list of allowed permissions/roles.
                         If a document ID is not present in the mapping, it is assumed public.
    :return: A list of accessible document IDs.
    """
    accessible = []
    for doc_id in document_ids:
        required_permissions = document_acl.get(doc_id)
        if required_permissions is None:
            # Public document
            accessible.append(doc_id)
        else:
            # Check if user has at least one of the required permissions
            if any(perm in user_permissions for perm in required_permissions):
                accessible.append(doc_id)
    return accessible
