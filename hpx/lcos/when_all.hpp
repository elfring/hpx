//  Copyright (c) 2007-2013 Hartmut Kaiser
//  Copyright (c) 2013 Agustin Berge
//
//  Distributed under the Boost Software License, Version 1.0. (See accompanying
//  file LICENSE_1_0.txt or copy at http://www.boost.org/LICENSE_1_0.txt)

#if !BOOST_PP_IS_ITERATING

#if !defined(HPX_LCOS_WHEN_ALL_APR_19_2012_1140AM)
#define HPX_LCOS_WHEN_ALL_APR_19_2012_1140AM

#include <hpx/hpx_fwd.hpp>
#include <hpx/lcos/future.hpp>
#include <hpx/lcos/when_n.hpp>
#include <hpx/util/always_void.hpp>
#include <hpx/util/decay.hpp>
#include <hpx/util/move.hpp>
#include <hpx/util/tuple.hpp>
#include <hpx/util/detail/pp_strip_parens.hpp>

#include <boost/preprocessor/cat.hpp>
#include <boost/preprocessor/enum.hpp>
#include <boost/preprocessor/iterate.hpp>

#include <algorithm>
#include <iterator>
#include <vector>

///////////////////////////////////////////////////////////////////////////////
namespace hpx { namespace lcos
{
    /// The function \a when_all is a operator allowing to join on the result
    /// of all given futures. It AND-composes all future objects given and
    /// returns a new future object representing the same list of futures
    /// after they finished executing.
    ///
    /// \note There are three variations of when_all. The first takes a pair
    ///       of InputIterators. The second takes an std::vector of future<R>.
    ///       The third takes any arbitrary number of future<R>, where R need
    ///       not be the same type.
    ///
    /// \return   Returns a future holding the same list of futures as has
    ///           been passed to when_all.
    ///           - future<vector<future<R>>>: If the input cardinality is
    ///             unknown at compile time and the futures are all of the
    ///             same type.
    ///           - future<tuple<future<R0>, future<R1>, future<R2>...>>: If
    ///             inputs are fixed in number and are of heterogeneous types.
    ///             The inputs can be any arbitrary number of future objects.

    template <typename Future>
    lcos::future<std::vector<Future> >
    when_all(std::vector<Future>& lazy_values,
        error_code& ec = throws)
    {
        typedef std::vector<Future> result_type;

        if (lazy_values.empty())
            return lcos::make_ready_future(result_type());

        return lcos::when_n(lazy_values.size(), lazy_values, ec);
    }

    template <typename Future>
    lcos::future<std::vector<Future> > //-V659
    when_all(std::vector<Future> && lazy_values,
        error_code& ec = throws)
    {
        return lcos::when_all(lazy_values, ec);
    }

    template <typename Iterator>
    lcos::future<std::vector<
        typename lcos::detail::future_iterator_traits<Iterator>::type
    > >
    when_all(Iterator begin, Iterator end, error_code& ec = throws)
    {
        typedef
            typename lcos::detail::future_iterator_traits<Iterator>::type
            future_type;
        typedef std::vector<future_type> result_type;

        result_type lazy_values_;
        std::transform(begin, end, std::back_inserter(lazy_values_),
            detail::when_acquire_future<future_type>());
        return lcos::when_all(lazy_values_, ec);
    }

    inline lcos::future<HPX_STD_TUPLE<> > //-V524
    when_all(error_code& /*ec*/ = throws)
    {
        typedef HPX_STD_TUPLE<> result_type;

        return lcos::make_ready_future(result_type());
    }
}}

#if !defined(HPX_USE_PREPROCESSOR_LIMIT_EXPANSION)
#  include <hpx/lcos/preprocessed/when_all.hpp>
#else

#if defined(__WAVE__) && defined(HPX_CREATE_PREPROCESSED_FILES)
#  pragma wave option(preserve: 1, line: 0, output: "preprocessed/when_all_" HPX_LIMIT_STR ".hpp")
#endif

#define BOOST_PP_ITERATION_PARAMS_1                                           \
    (3, (1, HPX_WAIT_ARGUMENT_LIMIT, <hpx/lcos/when_all.hpp>))                \
/**/
#include BOOST_PP_ITERATE()

#if defined(__WAVE__) && defined (HPX_CREATE_PREPROCESSED_FILES)
#  pragma wave option(output: null)
#endif

#endif // !defined(HPX_USE_PREPROCESSOR_LIMIT_EXPANSION)

namespace hpx
{
    using lcos::when_all;
}

#endif

///////////////////////////////////////////////////////////////////////////////
#else // BOOST_PP_IS_ITERATING

#define N BOOST_PP_ITERATION()

#define HPX_WHEN_N_DECAY_FUTURE(Z, N, D)                                      \
    typename util::decay<BOOST_PP_CAT(T, N)>::type                            \
    /**/

namespace hpx { namespace lcos
{
    ///////////////////////////////////////////////////////////////////////////
    template <BOOST_PP_ENUM_PARAMS(N, typename T)>
    lcos::future<HPX_STD_TUPLE<BOOST_PP_ENUM(N, HPX_WHEN_N_DECAY_FUTURE, _)> >
    when_all(HPX_ENUM_FWD_ARGS(N, T, f), error_code& ec = throws)
    {
        return lcos::when_n(N, HPX_ENUM_FORWARD_ARGS(N, T, f), ec);
    }
}}

#undef HPX_WHEN_N_DECAY_FUTURE
#undef N

#endif

